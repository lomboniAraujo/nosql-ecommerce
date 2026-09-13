# NoSQL E-commerce

Aplicación de comercio electrónico construida con una arquitectura NoSQL, pensada para escalar, manejar grandes volúmenes de datos y ofrecer una experiencia flexible para productos, usuarios, órdenes y pagos.

## Descripción general

Este proyecto implementa un sistema de e-commerce con almacenamiento en base de datos NoSQL, ideal para:
- Catálogos de productos con alta variabilidad
- Usuarios y perfiles dinámicos
- Carritos de compra y órdenes
- Consultas rápidas para búsqueda y filtros
- Escalabilidad horizontal

## Características

- Gestión de productos, categorías y marcas
- Registro e inicio de sesión de usuarios
- Carrito de compras persistente
- Procesamiento de pedidos
- Búsqueda por nombre, categoría, precio y atributos
- Soporte para múltiples colecciones/documentos
- Arquitectura preparada para crecimiento y alta concurrencia
- API REST para integración con frontend o apps móviles

## Stack tecnológico

- Lenguaje: JavaScript / TypeScript
- Backend: Node.js + Express
- Base de datos NoSQL: MongoDB
- ODM / cliente: Mongoose
- Autenticación: JWT
- Validación: Zod / Joi / Express Validator
- Gestión de dependencias: npm
- Testing: Jest / Vitest
- Documentación: Swagger (opcional)

## Estructura del proyecto

```bash
nosql-ecommerce/
├── src/
│   ├── config/
│   ├── controllers/
│   ├── middlewares/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── app.js
│   └── server.js
├── tests/
├── .env.example
├── .gitignore
├── package.json
├── README.md
└── docker-compose.yml
```

## Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

- Node.js 18+
- npm o yarn
- MongoDB local o Atlas
- Git

## Instalación

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd nosql-ecommerce
```

2. Instala las dependencias:
```bash
npm install
```

3. Configura las variables de entorno:
```bash
cp .env.example .env
```

4. Ajusta los valores en `.env`:
```env
PORT=3000
NODE_ENV=development
MONGODB_URI=mongodb://localhost:27017/nosql-ecommerce
JWT_SECRET=tu_secreto_super_seguro
JWT_EXPIRES_IN=7d
```

## Ejecución

Modo de desarrollo:
```bash
npm run dev
```

Modo de producción:
```bash
npm run build
npm start
```

## API REST

A continuación se muestran algunos endpoints típicos del sistema:

### Autenticación
- `POST /api/auth/register`
- `POST /api/auth/login`

### Usuarios
- `GET /api/users/:id`
- `PUT /api/users/:id`

### Productos
- `GET /api/products`
- `GET /api/products/:id`
- `POST /api/products`
- `PUT /api/products/:id`
- `DELETE /api/products/:id`

### Carrito
- `GET /api/cart`
- `POST /api/cart/items`
- `PUT /api/cart/items/:id`
- `DELETE /api/cart/items/:id`

### Ordenes
- `GET /api/orders`
- `POST /api/orders`
- `GET /api/orders/:id`

## Modelo de datos sugerido

### Usuarios
```json
{
    "id": "user_123",
    "name": "Ana García",
    "email": "ana@example.com",
    "passwordHash": "hashed_password",
    "role": "customer",
    "createdAt": "2025-01-15T10:00:00Z"
}
```

### Productos
```json
{
    "id": "prod_456",
    "name": "Smartphone X",
    "slug": "smartphone-x",
    "description": "Teléfono inteligente con cámara avanzada",
    "price": 699.99,
    "stock": 25,
    "category": "electronics",
    "tags": ["smartphone", "android", "5g"],
    "attributes": {
        "brand": "TechBrand",
        "color": "black",
        "memory": "128GB"
    }
}
```

### Ordenes
```json
{
    "id": "order_789",
    "userId": "user_123",
    "items": [
        {
            "productId": "prod_456",
            "quantity": 1,
            "price": 699.99
        }
    ],
    "status": "paid",
    "total": 699.99,
    "createdAt": "2025-01-16T09:30:00Z"
}
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `PORT` | Puerto del servidor |
| `NODE_ENV` | Entorno de ejecución |
| `MONGODB_URI` | Cadena de conexión a MongoDB |
| `JWT_SECRET` | Clave para firmar tokens JWT |
| `JWT_EXPIRES_IN` | Tiempo de expiración del token |

## Scripts disponibles

```json
{
    "scripts": {
        "dev": "nodemon src/server.js",
        "start": "node src/server.js",
        "build": "tsc",
        "test": "jest"
    }
}
```

## Testing

Ejecuta la suite de pruebas:
```bash
npm test
```

Puedes añadir pruebas unitarias e integración para:
- autenticación
- catálogo de productos
- carrito
- órdenes
- validaciones

## Seguridad

Se recomienda:
- Usar `JWT` con expiración
- Hashear contraseñas con bcrypt
- Validar todos los inputs del cliente
- Usar CORS y Helmet
- Evitar exposición de información sensible
- Configurar variables de entorno seguras

## Despliegue

Este proyecto puede desplegarse en:
- Vercel
- Render
- Railway
- Docker + VPS
- Kubernetes

Con MongoDB Atlas o una instancia de MongoDB en la nube.

## Contribución

1. Haz fork del proyecto
2. Crea una rama para tu funcionalidad:
```bash
git checkout -b feature/nueva-funcionalidad
```
3. Realiza tus cambios
4. Haz commit:
```bash
git commit -m "Agregar nueva funcionalidad"
```
5. Haz push:
```bash
git push origin feature/nueva-funcionalidad
```
6. Abre un Pull Request

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Para más detalles, consulta el archivo `LICENSE`.

## Contacto

Si deseas colaborar o tienes dudas, puedes contactarte con el responsable del proyecto o abrir un issue en el repositorio.

---

Hecho con ❤️ para un e-commerce escalable con NoSQL.
