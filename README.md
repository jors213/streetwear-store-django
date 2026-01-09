# Gengar Store | Cyber-Urban E-commerce 🟣

> **Una plataforma de comercio electrónico inmersiva diseñada para la moda streetwear de alta gama.**

## 💼 El Negocio y el Desafío

**Gengar Store** nace de la necesidad de fusionar la identidad visual del *Streetwear* (estética Cyberpunk/Dark) con una experiencia de compra técnica y robusta. Las tiendas convencionales carecen de personalidad y muchas veces fallan al gestionar "Drops" (lanzamientos) de productos exclusivos con stock limitado.

**El objetivo:** Desarrollar una aplicación web Fullstack que no solo sirva como catálogo, sino que gestione el ciclo completo de venta: desde la selección visual de tallas y validación de stock en tiempo real, hasta el procesamiento seguro de pagos bancarios y el seguimiento post-venta.

## 🚀 Impacto y Solución Entregada

Se desarrolló una solución a medida que aborda puntos críticos del e-commerce moderno:

* **Integridad de Stock (Concurrencia):** Implementación de transacciones atómicas y bloqueos pesimistas (`select_for_update`) en la base de datos. Esto evita que dos usuarios compren el último artículo simultáneamente durante un lanzamiento de alta demanda.
* **Pagos Reales:** Integración completa con la pasarela **Webpay Plus (Transbank)** utilizando el SDK oficial, manejando flujos de éxito, rechazo y anulación de compra con retorno de stock automático.
* **Experiencia de Usuario (UX/UI):** Diseño "Cyber-Luxury" personalizado (sin plantillas genéricas) enfocado en *Mobile First*, con animaciones fluidas y modo oscuro nativo para resaltar la fotografía de producto.

## 🛠️ Stack Tecnológico

Este proyecto fue construido priorizando el control total sobre el código y la escalabilidad:

* **Backend:** Python 3.11 + **Django 5** (Framework de alto nivel para seguridad y rapidez).
* **Frontend:** HTML5 + CSS3 Moderno (Variables CSS, Flexbox/Grid) + JavaScript Vanilla (Lógica de cliente ligera).
* **Base de Datos:** SQLite (Entorno de Desarrollo) / Compatible con PostgreSQL.
* **API & Integraciones:**
    * **Django REST Framework:** API endpoints para validación de pagos y escalabilidad futura a App Móvil.
    * **Transbank SDK:** Procesamiento de tarjetas de crédito/débito en Chile.
    * **SMTP:** Sistema de notificaciones por correo electrónico.

## 📸 Galería

<img width="1903" height="913" alt="GaleriaWebEcommerce" src="https://github.com/user-attachments/assets/115f7e0e-a192-430a-9da3-ea0fb7a81211" />
<img width="1900" height="914" alt="PortadaWebEcommerce" src="https://github.com/user-attachments/assets/bede687a-0bbe-4867-9df5-b17d4c8f7b59" />
<img width="1894" height="917" alt="GaleriaWebEcommerce1" src="https://github.com/user-attachments/assets/281981cd-bd10-4ea4-badf-d8037d5ac0a0" />
<img width="1899" height="822" alt="GaleriaWebEcommerce2" src="https://github.com/user-attachments/assets/a5f50bad-a449-4ce2-b79c-3cbfd5980ae0" />
<img width="1914" height="910" alt="GaleriaWebEcommerce6" src="https://github.com/user-attachments/assets/452e092d-170c-433f-96aa-f3ea549b3a14" />
<img width="1914" height="910" alt="GaleriaWebEcommerce7" src="https://github.com/user-attachments/assets/03630353-03b3-45c0-977f-b2d1b832a345" />
<img width="1916" height="915" alt="GaleriaWebEcommerce4" src="https://github.com/user-attachments/assets/0941a5a9-bbf9-4b49-bfe3-be5f7be31200" />
<img width="1914" height="918" alt="GaleriaWebEcommerce8" src="https://github.com/user-attachments/assets/4c866935-e0f0-44ae-ae15-8620d04b7387" />
<img width="1895" height="915" alt="GaleriaWebEcommerce3" src="https://github.com/user-attachments/assets/0dcf2bad-2aa9-43e4-855b-b4ac2a063398" />
<img width="1914" height="918" alt="GaleriaWebEcommerce9" src="https://github.com/user-attachments/assets/faa4af4b-122c-4e93-9d2f-2410debf16c4" />
<img width="1900" height="883" alt="GaleriaWebEcommerce5" src="https://github.com/user-attachments/assets/48340719-1994-4c02-af1f-4a90bb435dd2" />
<img width="1914" height="918" alt="GaleriaWebEcommerce10" src="https://github.com/user-attachments/assets/a583231d-b6c5-4837-8921-990768bb2ede" />



## 🔧 Ejecución Local (Para Desarrolladores)

Si deseas levantar este proyecto en tu entorno local para pruebas o contribución:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/streetwear-store-django.git](https://github.com/tu-usuario/streetwear-store-django.git)
    cd streetwear-store-django
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuración:**
    Crea un archivo `.env` en la raíz (puedes basarte en un `.env.example`) para tus claves secretas y configuración de Webpay (si usas modo integración, Django usará las de prueba por defecto).

5.  **Ejecutar migraciones y servidor:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos y de portafolio profesional.
**Designed & Developed by Jorge - 2026.**
