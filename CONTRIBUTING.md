# Contribuciones al Sistema de Gestión de Flota

¡Gracias por tu interés en contribuir al Sistema de Gestión de Flota de Vehículos! Este documento te guiará en el proceso de contribución.

## 🤝 Cómo Contribuir

### 1. Fork del Repositorio
1. Haz fork del repositorio en GitHub
2. Clona tu fork localmente:
```bash
git clone https://github.com/tu-usuario/formulario-solicitudes.git
cd formulario-solicitudes
```

### 2. Configuración del Entorno de Desarrollo

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Inicializar Base de Datos
```bash
python init_db.py
```

### 3. Crear una Rama para tu Feature
```bash
git checkout -b feature/nombre-de-tu-feature
```

### 4. Realizar Cambios

#### Estructura de Commits
- Usa commits descriptivos en español
- Formato: `tipo: descripción breve`
- Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Ejemplos:
```
feat: agregar endpoint para mantenimientos preventivos
fix: corregir validación de fechas en asignaciones
docs: actualizar documentación de API de vehículos
```

### 5. Testing
```bash
# Ejecutar pruebas básicas
python test_simple.py

# Ejecutar pruebas del sistema
python test_system.py
```

### 6. Documentación
- Actualiza la documentación relevante
- Asegúrate de que el código esté comentado
- Actualiza el CHANGELOG.md si es necesario

### 7. Pull Request
1. Push a tu rama:
```bash
git push origin feature/nombre-de-tu-feature
```
2. Crea un Pull Request en GitHub
3. Describe claramente los cambios realizados

## 📋 Estándares de Código

### Python (Backend)
- Sigue PEP 8
- Usa type hints
- Documenta funciones y clases:
```python
def crear_vehiculo(vehiculo_data: VehiculoCreate) -> Vehiculo:
    """
    Crea un nuevo vehículo en el sistema.
    
    Args:
        vehiculo_data: Datos del vehículo a crear
        
    Returns:
        Vehiculo: El vehículo creado
        
    Raises:
        ValueError: Si los datos son inválidos
    """
```

### TypeScript (Frontend - Futuro)
- Usa ESLint y Prettier
- Componentes funcionales con hooks
- Tipado estricto

### Base de Datos
- Usa migraciones para cambios de esquema
- Nombres en español para coherencia
- Relaciones bien definidas

## 🗂️ Tipos de Contribuciones

### 🐛 Reportar Bugs
Usa el template de issue para bugs:
- Descripción clara del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots si aplica

### 💡 Sugerir Features
- Describe el caso de uso
- Explica el beneficio para los usuarios
- Considera la complejidad de implementación

### 📝 Documentación
- Mejoras en claridad
- Ejemplos adicionales
- Correcciones de traducción
- Nuevas guías

### 🔧 Desarrollo
#### Features Prioritarios:
1. **Frontend React**: Interfaz de usuario completa
2. **Aplicación Móvil**: Para conductores y supervisores
3. **Reportes Avanzados**: Dashboard con métricas
4. **Integración WhatsApp**: Notificaciones automáticas
5. **Módulo de Combustible**: Control de gastos

#### Áreas de Mejora:
- Optimización de rendimiento
- Seguridad adicional
- Tests automatizados
- Dockerización
- CI/CD Pipeline

## 🚀 Proceso de Review

### Criterios de Aceptación
- [ ] El código sigue los estándares establecidos
- [ ] Incluye tests apropiados
- [ ] La documentación está actualizada
- [ ] No hay errores de linting
- [ ] Funciona correctamente en local

### Timeline
- Reviews iniciales: 2-3 días
- Implementación de cambios: Según complejidad
- Merge: 1-2 días después de aprobación

## 📞 Comunicación

### Canales
- **Issues**: Para bugs y features
- **Discussions**: Para preguntas generales
- **Pull Requests**: Para código específico

### Etiquetas
- `bug`: Errores del sistema
- `enhancement`: Nuevas características
- `documentation`: Mejoras de docs
- `good-first-issue`: Para nuevos contribuyentes
- `help-wanted`: Necesita ayuda externa
- `priority-high`: Requiere atención urgente

## 🎯 Roadmap de Contribuciones

### Corto Plazo (1-2 meses)
- [ ] Frontend básico con React
- [ ] Tests automatizados
- [ ] Dockerización del backend
- [ ] Documentación API completa

### Mediano Plazo (3-6 meses)
- [ ] Aplicación móvil
- [ ] Dashboard avanzado
- [ ] Integración con servicios externos
- [ ] Módulos adicionales

### Largo Plazo (6+ meses)
- [ ] Escalabilidad mejorada
- [ ] IA para asignación inteligente
- [ ] Integración con sistemas municipales
- [ ] Multi-tenancy

## 🏆 Reconocimientos

Los contribuyentes serán reconocidos en:
- README.md del proyecto
- Changelog de releases
- Documentación de créditos

### Tipos de Contribuciones Valoradas
- Código (desarrollo de features)
- Documentación (guías, ejemplos)
- Testing (casos de prueba)
- Diseño (UI/UX)
- Feedback (testing de funcionalidades)

## ❓ Preguntas Frecuentes

### ¿Puedo contribuir sin experiencia previa?
Sí, tenemos issues marcados como `good-first-issue` perfectos para comenzar.

### ¿Qué tecnologías necesito conocer?
- **Mínimo**: Python, FastAPI, SQLAlchemy
- **Deseable**: React, TypeScript, PostgreSQL
- **Plus**: Docker, Azure/AWS, React Native

### ¿Cómo propongo cambios mayores?
1. Crea un issue de tipo "proposal"
2. Describe la idea detalladamente
3. Espera feedback antes de implementar

### ¿Hay algún código de conducta?
Sí, seguimos las mejores prácticas de open source:
- Respeto mutuo
- Comunicación constructiva
- Inclusión y diversidad
- Enfoque en soluciones

---

## 🚀 ¡Empezar a Contribuir!

1. **Explora el código**: Familiarízate con la estructura
2. **Lee la documentación**: Especialmente MANUAL_COMPLETO.md
3. **Busca un issue**: Filtra por `good-first-issue`
4. **Pregunta**: No dudes en hacer preguntas
5. **¡Contribuye!**: Tu aporte es valioso

¡Esperamos tus contribuciones para hacer de este sistema una herramienta aún mejor para la gestión municipal de flotas vehiculares!

---
*Última actualización: Enero 2025*