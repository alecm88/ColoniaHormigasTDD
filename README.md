# ColoniaHormigasTDD
Grupo 3: Simulacion TDD de Colonia hormigas. Subsistema Hormiga Reina

Asignación Proyecto de Calidad y Pruebas de Software para la Simulación de una Colonia de Hormigas (enfoque TDD) 
El presente documento describe el proyecto de simulación de una colonia de hormigas. El objetivo principal es crear un sistema modular compuesto por cinco subsistemas, cada uno encargado de modelar una función y dominio específicos dentro de la colonia. Cada subsistema expondrá APIs para la comunicación/interacción y deberá contar con pruebas unitarias automatizadas desarrolladas siguiendo TDD y con reporte de cobertura. La simulación brindará una herramienta educativa para comprender mejor el comportamiento y organización de las colonias, y para evidenciar prácticas de calidad. 

3. Alcance del Proyecto 
El proyecto se centrará en el desarrollo de un software modular compuesto por el siguientes subsistema:

3.1 Subsistema de Hormiga Reina 
Responsable de modelar el comportamiento de la hormiga reina y controlar la generación y asignación de nuevas hormigas. Expone una API para solicitud/asignación. 
Requisitos funcionales mínimos: 
•	Crear hormigas bajo demanda con capacidad máxima (p. ej., configurable, default 100). 
•	Asignar hormigas a subsistemas solicitantes (Comunicación, Recolección, Defensa) según prioridad. 
Requisitos de calidad/pruebas: 
•	TDD para reglas de capacidad, prioridad y asignación. 
•	Pruebas unitarias para: creación válida/ inválida, rechazo al exceder capacidad, reasignación. 
•	Cobertura ≥ 80% en este módulo. 

Stretch Goals 
•	Expiración de hormigas: cada hormiga tiene time-to-live (puede expirar en medio de una función). 
•	Manejo de crisis: priorizar creación de hormigas ante ataques y pausar recolección. 
•	Inyección de fallas: simular fallos de API/latencia para robustez (con pruebas).
