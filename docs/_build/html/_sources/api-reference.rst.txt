API Reference
============

Esta sección documenta la API de SQL for Testers.

Endpoints Principales
-------------------

Autenticación
~~~~~~~~~~~~

.. http:post:: /register

   Registra un nuevo usuario.

   **Request JSON Object**

   - ``email`` (string) - Email del usuario
   - ``password`` (string) - Contraseña
   - ``firstName`` (string) - Nombre
   - ``lastName`` (string) - Apellido

   **Response**

   - 201 Created
   - 400 Bad Request (si el email ya existe)

.. http:post:: /login

   Inicia sesión de usuario.

   **Request JSON Object**

   - ``email`` (string) - Email del usuario
   - ``password`` (string) - Contraseña

   **Response**

   - 200 OK
   - 401 Unauthorized (credenciales inválidas)

Lecciones
~~~~~~~~

.. http:get:: /lessons

   Obtiene todas las lecciones disponibles.

   **Response**

   - 200 OK
   - Array de lecciones con:
     - ``id`` (integer)
     - ``title`` (string)
     - ``description`` (string)
     - ``difficulty`` (string)

.. http:get:: /lessons/:id

   Obtiene una lección específica.

   **Response**

   - 200 OK
   - Objeto de lección con:
     - ``id`` (integer)
     - ``title`` (string)
     - ``content`` (string)
     - ``exercises`` (array)

Ejercicios
~~~~~~~~~

.. http:post:: /exercises/:id/execute

   Ejecuta un ejercicio SQL.

   **Request JSON Object**

   - ``query`` (string) - Consulta SQL a ejecutar

   **Response**

   - 200 OK
   - Objeto con:
     - ``success`` (boolean)
     - ``results`` (array)
     - ``error`` (string, opcional)

Base de Datos
------------

La aplicación utiliza SQLite como base de datos. Las tablas principales son:

users
~~~~~

.. code-block:: sql

   CREATE TABLE users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       email TEXT UNIQUE NOT NULL,
       password TEXT NOT NULL,
       firstName TEXT NOT NULL,
       lastName TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

lessons
~~~~~~~

.. code-block:: sql

   CREATE TABLE lessons (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       description TEXT,
       content TEXT,
       difficulty TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

exercises
~~~~~~~~~

.. code-block:: sql

   CREATE TABLE exercises (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       lesson_id INTEGER,
       title TEXT NOT NULL,
       description TEXT,
       solution TEXT,
       FOREIGN KEY (lesson_id) REFERENCES lessons(id)
   ); 