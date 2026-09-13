import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

try:
    import redis
except Exception:  # pragma: no cover
    redis = None

try:
    from pymongo import MongoClient
except Exception:  # pragma: no cover
    MongoClient = None

try:
    from cassandra.cluster import Cluster
except Exception:  # pragma: no cover
    Cluster = None

try:
    from neo4j import GraphDatabase
except Exception:  # pragma: no cover
    GraphDatabase = None


@dataclass
class Product:
    sku: str
    name: str
    price: float
    category: str
    stock: int
    created_at: str | None = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    country: str


class MultiModelECommerceEngine:
    def __init__(self) -> None:
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.cassandra_hosts = os.getenv("CASSANDRA_HOSTS", "127.0.0.1").split(",")
        self.cassandra_keyspace = os.getenv("CASSANDRA_KEYSPACE", "ecommerce")
        self.neo4j_url = os.getenv("NEO4J_URL", "neo4j://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

        self.redis_client = self._init_redis()
        self.mongo_client = self._init_mongo()
        self.cassandra_cluster = None
        self.cassandra_session = self._init_cassandra()
        self.neo4j_driver = self._init_neo4j()

    def _init_redis(self):
        if redis is None:
            return None
        try:
            return redis.Redis.from_url(self.redis_url, decode_responses=True)
        except Exception:
            return None

    def _init_mongo(self):
        if MongoClient is None:
            return None
        try:
            return MongoClient(self.mongo_url, serverSelectionTimeoutMS=2000)
        except Exception:
            return None

    def _init_cassandra(self):
        if Cluster is None:
            return None
        try:
            cluster = Cluster(self.cassandra_hosts, port=9042)
            self.cassandra_cluster = cluster
            session = cluster.connect()
            self._ensure_cassandra_keyspace(session)
            session.set_keyspace(self.cassandra_keyspace)
            self._ensure_cassandra_schema(session)
            return session
        except Exception:
            return None

    def _init_neo4j(self):
        if GraphDatabase is None:
            return None
        try:
            return GraphDatabase.driver(self.neo4j_url, auth=(self.neo4j_user, self.neo4j_password))
        except Exception:
            return None

    def _ensure_cassandra_keyspace(self, session) -> None:
        session.execute(
            f"CREATE KEYSPACE IF NOT EXISTS {self.cassandra_keyspace} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}"
        )

    def _ensure_cassandra_schema(self, session) -> None:
        session.execute(
            "CREATE TABLE IF NOT EXISTS product_views ("
            "customer_id text, product_sku text, viewed_at text, PRIMARY KEY ((customer_id), viewed_at, product_sku))"
        )
        session.execute(
            "CREATE TABLE IF NOT EXISTS orders ("
            "order_id text, customer_id text, product_sku text, quantity int, total double, created_at text, PRIMARY KEY (order_id, created_at))"
        )

    def create_product(self, product: Product) -> dict[str, Any]:
        payload = asdict(product)
        if self.redis_client is not None:
            self.redis_client.hset(f"product:{product.sku}", mapping=payload)
            self.redis_client.expire(f"product:{product.sku}", 3600)

        if self.mongo_client is not None:
            db = self.mongo_client["ecommerce"]
            db.products.replace_one({"sku": product.sku}, payload, upsert=True)

        if self.cassandra_session is not None:
            self.cassandra_session.execute(
                "INSERT INTO product_views (customer_id, product_sku, viewed_at) VALUES (%s, %s, %s)",
                ("system", product.sku, product.created_at),
            )

        return payload

    def create_customer(self, customer: Customer) -> dict[str, Any]:
        if self.mongo_client is not None:
            db = self.mongo_client["ecommerce"]
            db.customers.replace_one({"customer_id": customer.customer_id}, asdict(customer), upsert=True)

        if self.redis_client is not None:
            self.redis_client.hset(f"customer:{customer.customer_id}", mapping=asdict(customer))

        return asdict(customer)

    def add_to_cart(self, customer_id: str, sku: str, quantity: int = 1) -> dict[str, Any]:
        cart_key = f"cart:{customer_id}"
        item = {"sku": sku, "quantity": quantity}
        if self.redis_client is not None:
            self.redis_client.hset(cart_key, sku, str(quantity))

        return {"customer_id": customer_id, "sku": sku, "quantity": quantity, "cart_key": cart_key}

    def record_product_view(self, customer_id: str, product_sku: str) -> dict[str, Any]:
        viewed_at = datetime.now(timezone.utc).isoformat()
        if self.cassandra_session is not None:
            self.cassandra_session.execute(
                "INSERT INTO product_views (customer_id, product_sku, viewed_at) VALUES (%s, %s, %s)",
                (customer_id, product_sku, viewed_at),
            )

        return {"customer_id": customer_id, "product_sku": product_sku, "viewed_at": viewed_at}

    def create_order(self, order_id: str, customer_id: str, product_sku: str, quantity: int, unit_price: float) -> dict[str, Any]:
        created_at = datetime.now(timezone.utc).isoformat()
        total = round(quantity * unit_price, 2)

        if self.cassandra_session is not None:
            self.cassandra_session.execute(
                "INSERT INTO orders (order_id, customer_id, product_sku, quantity, total, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (order_id, customer_id, product_sku, quantity, total, created_at),
            )

        if self.neo4j_driver is not None:
            with self.neo4j_driver.session() as session:
                session.run(
                    "MERGE (c:Customer {customer_id: $customer_id}) "
                    "MERGE (p:Product {sku: $product_sku}) "
                    "MERGE (c)-[:PURCHASED {order_id: $order_id, quantity: $quantity, total: $total, created_at: $created_at}]->(p)",
                    customer_id=customer_id,
                    product_sku=product_sku,
                    order_id=order_id,
                    quantity=quantity,
                    total=total,
                    created_at=created_at,
                )

        return {
            "order_id": order_id,
            "customer_id": customer_id,
            "product_sku": product_sku,
            "quantity": quantity,
            "total": total,
            "created_at": created_at,
        }

    def recommend_products_for_customer(self, customer_id: str) -> list[str]:
        if self.neo4j_driver is None:
            return []

        with self.neo4j_driver.session() as session:
            result = session.run(
                "MATCH (c:Customer {customer_id: $customer_id})-[:PURCHASED]->(p:Product)<-[:PURCHASED]-(other:Customer) "
                "WITH other, p, COUNT(*) AS commonality "
                "MATCH (other)-[:PURCHASED]->(recommended:Product) "
                "WHERE recommended.sku <> p.sku "
                "RETURN DISTINCT recommended.sku AS sku LIMIT 5",
                customer_id=customer_id,
            )
            return [record["sku"] for record in result]

    def close(self) -> None:
        if self.redis_client is not None:
            self.redis_client.close()
        if self.mongo_client is not None:
            self.mongo_client.close()
        if self.cassandra_session is not None:
            try:
                self.cassandra_session.shutdown()
            except AttributeError:
                pass
        if self.cassandra_cluster is not None:
            try:
                self.cassandra_cluster.shutdown()
            except Exception:
                pass
        if self.neo4j_driver is not None:
            self.neo4j_driver.close()


if __name__ == "__main__":
    engine = MultiModelECommerceEngine()

    laptop = Product(sku="LAPTOP-100", name="Nimbus Laptop", price=1299.99, category="electronics", stock=42)
    mouse = Product(sku="MOUSE-200", name="Orbit Mouse", price=39.99, category="accessories", stock=120)
    customer = Customer(customer_id="C-1001", name="Alice Johnson", email="alice@example.com", country="US")

    print(engine.create_product(laptop))
    print(engine.create_product(mouse))
    print(engine.create_customer(customer))
    print(engine.add_to_cart(customer.customer_id, laptop.sku, 1))
    print(engine.record_product_view(customer.customer_id, laptop.sku))
    print(engine.create_order("ORD-5001", customer.customer_id, laptop.sku, 1, laptop.price))
    print(engine.create_order("ORD-5002", customer.customer_id, mouse.sku, 2, mouse.price))
    print(engine.recommend_products_for_customer(customer.customer_id))

    engine.close()
