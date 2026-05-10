# LEGAL — Plantilla contractual y consideraciones

> Este documento es una **plantilla orientativa**, no asesoría legal.
> El cliente final debe validar los textos con su equipo legal antes de
> incorporarlos a sus políticas internas o términos contractuales.

## 1. Cláusula sugerida para política interna del cliente

```
Política de Entrenamiento en Sparring Conversacional contra Ingeniería Social

1. Naturaleza voluntaria.
   La participación en sesiones de sparring conversacional contra
   ingeniería social en la plataforma CiberSpar es estrictamente
   voluntaria. Ningún colaborador puede ser sancionado por declinar
   participar, abandonar una sesión en curso, o por el resultado de su
   sesión.

2. Confidencialidad individual.
   Los resultados individuales de cualquier sesión de sparring no serán
   compartidos con jefaturas, recursos humanos, ni con la organización
   bajo ninguna circunstancia. La organización solo recibirá métricas
   agregadas con un mínimo de diez (10) participantes por bucket
   estadístico, conforme al diseño técnico de la plataforma.

3. Efemeridad de los datos.
   Las conversaciones, los modelos de defensa derivados y cualquier
   contenido generado durante una sesión se eliminan automáticamente al
   cerrar la sesión o al cumplirse treinta (30) minutos desde su inicio,
   lo que ocurra primero. La organización no posee mecanismos para
   recuperar dicha información después del cierre.

4. Salida sin estigma.
   El uso del botón "Salir con dignidad" durante una sesión no constituye
   abandono ni incumplimiento. La organización reconoce explícitamente
   que la decisión de pausar es legítima y que no será considerada
   negativamente en evaluaciones de desempeño.

5. Uso pedagógico exclusivo.
   La plataforma se utiliza exclusivamente para fines formativos. Queda
   expresamente prohibido cualquier uso orientado a evaluar individualmente
   a colaboradores, vigilar su comportamiento, o construir perfiles
   psicológicos.

6. Reporte y derecho de oposición.
   Cualquier colaborador que considere que un uso de la plataforma se
   aparta de esta política puede reportarlo al Delegado de Protección de
   Datos / Oficial de Cumplimiento de la organización, sin que esto
   implique consecuencia adversa.
```

## 2. Cumplimiento con la Ley Orgánica de Protección de Datos Personales (LOPDP) de Ecuador

CiberSpar fue diseñado con el siguiente mapeo a la LOPDP:

| Principio LOPDP | Cómo se cumple en CiberSpar |
|------------------|------------------------------|
| Licitud | Consentimiento explícito al inicio (checkbox de onboarding). |
| Finalidad | Una sola finalidad: entrenamiento andragógico voluntario. |
| Lealtad y transparencia | Se le dice al usuario, en lenguaje no técnico, qué pasa con sus datos y se le ofrece "Verificar borrado". |
| Minimización | No se procesa OSINT del usuario. Se procesa solo el contenido que él voluntariamente envía. |
| Calidad | El contenido procesado existe en RAM/Redis y se descarta a los 30 minutos. |
| Conservación limitada | TTL técnico = 30 minutos. Codificado en `Settings` con guard rail que rechaza prod con TTL mayor. |
| Seguridad | TLS en tránsito, cifrado en reposo de Redis y Postgres a nivel de despliegue, autenticación de facilitador. |
| Responsabilidad demostrada | Tests automatizados que verifican la ephemerality y el threshold n≥10. |

### Elementos a cubrir en el contrato cliente-proveedor

1. **Identificación de los responsables y encargados del tratamiento**
   (cliente final = responsable; HackTheMinds / proveedor de la plataforma
   = encargado).
2. **Finalidad del tratamiento**: única — entrenamiento.
3. **Categorías de datos tratados**: contenido conversacional efímero
   producido por el usuario durante la sesión. Sin datos sensibles
   solicitados.
4. **Plazo de conservación**: 30 minutos máximo en Redis (TTL técnico).
5. **Medidas técnicas y organizativas**: las descritas en este repositorio
   y en el README (TTL forzado, n≥10, safety_filter, sin OSINT).
6. **Subencargados**: Anthropic (procesamiento del modelo). El cliente
   debe estar informado y consentir.
7. **Derecho del titular**: acceso, rectificación, supresión y oposición.
   Dado el diseño efímero, el ejercicio del derecho de supresión es
   automático y verificable a los 30 minutos.

## 3. Líneas rojas no negociables que el cliente final debe aceptar

El cliente que adquiere CiberSpar debe aceptar contractualmente:

1. **No solicitar conversaciones individuales** de colaboradores, ni
   en formato exportado ni mediante cualquier otra vía. La plataforma no
   provee este endpoint y no se desarrollará uno.
2. **No solicitar identificación de colaboradores** asociada a resultados
   individuales. Las métricas son siempre agregadas n≥10.
3. **No usar resultados como base para sanciones** disciplinarias,
   evaluaciones de desempeño o decisiones de empleo.
4. **No replicar conversaciones reales** de personas reales (clientes,
   proveedores, ejecutivos) en personajes corporativos. Solo arquetipos
   de rol.
5. **No usar la plataforma como herramienta de pre-incidente** para
   inducir conductas en colaboradores específicos.

El uso de la plataforma para cualquiera de los fines anteriores constituye
incumplimiento contractual grave y faculta al proveedor a suspender el
servicio inmediatamente.

## 4. Aviso de privacidad sugerido para mostrar al colaborador

```
Este simulador entrena tu defensa frente a ingeniería social en
conversaciones efímeras. Mientras conversas:

- Lo que escribes existe solo en memoria temporal del servidor.
- A los 30 minutos, todo se borra automáticamente.
- Tus respuestas individuales no se comparten con tu empleador.
- Tu empleador solo verá estadísticas agregadas con al menos 10 personas
  participantes en el mismo grupo.
- Puedes salir en cualquier momento sin consecuencias.
- Al final, podrás verificar técnicamente que se borró todo.
```
