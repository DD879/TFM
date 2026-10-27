Informe de auditoría de seguridad — Reentrance
1 vulnerabilidad crítica
Análisis estático manual

Contrato: Reentrance
Versión Solidity: ^0.4.15
Alcance: exclusivamente el código proporcionado.
Metodología: análisis del flujo de ejecución, llamadas externas y modificaciones de estado. No se ha realizado compilación, despliegue ni ejecución de pruebas.
1. Resumen ejecutivo
Se identifica una vulnerabilidad de reentrancia (SWC-107) en la función withdrawBalance().

La función realiza una transferencia de Ether mediante una llamada externa antes de actualizar el saldo interno del usuario. Esto permite que un contrato receptor, si dispone de una función de recepción adecuada, vuelva a invocar withdrawBalance() mientras su saldo todavía mantiene el valor anterior.

El resultado potencial es la retirada repetida de fondos y el consumo de Ether perteneciente a otros depositantes.
Identificador	Categoría	SWC	Severidad	Confianza
RE-01	Reentrancia	SWC-107	Crítica	Confirmado por el código

Resultado: 1 vulnerabilidad de seguridad justificada. No se identifican otros hallazgos de seguridad independientes con evidencia suficiente en el código proporcionado.
2. Hallazgo RE-01 — Reentrancia en retirada de fondos
Categoría: Reentrancia (Reentrancy).

Código SWC: SWC-107.

Función afectada: withdrawBalance().

Ubicación: líneas 14–19, numerando las líneas no vacías y vacías del contrato desde pragma solidity como línea 1, sin contar los espacios iniciales del mensaje. Las instrucciones relevantes son:
if( ! (msg.sender.call.value(userBalance[msg.sender])() ) ){
    throw;
}
userBalance[msg.sender] = 0;


2.1. Causa técnica
La vulnerabilidad se produce porque el contrato incumple el patrón Checks-Effects-Interactions.

La instrucción:
msg.sender.call.value(userBalance[msg.sender])()


realiza una llamada externa de bajo nivel que puede transferir Ether y ceder el control de ejecución al contrato receptor.

Durante esta llamada, el saldo registrado en userBalance[msg.sender] todavía no ha sido actualizado.

La actualización:
userBalance[msg.sender] = 0;


se realiza únicamente después de que la llamada externa haya finalizado correctamente.

Por tanto, un contrato receptor puede volver a invocar la función antes de que su saldo sea puesto a cero.
2.2. Condiciones necesarias
Para que la vulnerabilidad pueda explotarse con consecuencias económicas, deben cumplirse las siguientes condiciones:
1. El receptor de la transferencia debe ser un contrato capaz de ejecutar lógica durante la recepción de Ether.
2. Dicho contrato debe tener un saldo positivo registrado en userBalance.
3. Debe producirse una llamada reentrante a withdrawBalance() antes de que termine la llamada externa original.
4. El contrato Reentrance debe disponer de Ether suficiente para satisfacer retiradas adicionales.
Estas condiciones son compatibles con el código analizado. Sin embargo, no se ha comprobado su explotación mediante ejecución real.
2.3. Impacto potencial
La explotación permitiría retirar repetidamente el saldo registrado de un mismo usuario antes de que este se actualice.

Esto puede provocar:
- Retirada de Ether superior al saldo legítimo del atacante.
- Pérdida de fondos depositados por otros usuarios.
- Desajuste entre los saldos internos y el Ether disponible.
- Imposibilidad de atender posteriormente retiradas legítimas.
Severidad: crítica.

La clasificación se justifica por la posibilidad de comprometer fondos de terceros y agotar el Ether disponible en el contrato, sin requerir privilegios administrativos.

La severidad corresponde al impacto potencial del defecto, no a una explotación demostrada en una instancia desplegada.
2.4. Mitigación propuesta
Se recomienda aplicar el patrón Checks-Effects-Interactions, actualizando el saldo antes de efectuar cualquier transferencia externa.

También se debe verificar explícitamente que el usuario dispone de un saldo positivo.

Código corregido compatible con Solidity ^0.4.15:
pragma solidity ^0.4.15;

contract Reentrance {
    mapping(address => uint) userBalance;

    function getBalance(address u)
        constant
        returns (uint)
    {
        return userBalance[u];
    }

    function addToBalance() payable {
        userBalance[msg.sender] += msg.value;
    }

    function withdrawBalance() {
        uint amount = userBalance[msg.sender];

        require(amount > 0);

        userBalance[msg.sender] = 0;

        if (!msg.sender.call.value(amount)()) {
            throw;
        }
    }
}


Justificación de la corrección:

La modificación principal consiste en ejecutar:
userBalance[msg.sender] = 0;


antes de transferir Ether.

De esta manera, si el receptor intenta volver a ejecutar withdrawBalance(), encontrará su saldo actualizado a cero y no podrá retirar nuevamente el mismo importe.

Si la transferencia falla, throw revierte la transacción, incluida la modificación previa del saldo.

La corrección mantiene la compatibilidad sintáctica con Solidity 0.4.15. No obstante, debe verificarse mediante compilación y pruebas antes de utilizarse en producción.

Confianza: confirmado por el código.

La existencia del patrón vulnerable es inequívoca. La explotación práctica y el importe potencialmente sustraíble dependen del estado y saldo del contrato en ejecución.
3. Observaciones adicionales no clasificadas como vulnerabilidades independientes
Observación	Clasificación	Justificación
Uso de throw	Buena práctica	Puede sustituirse por require en determinadas comprobaciones, aunque su uso no constituye por sí mismo una vulnerabilidad.
Uso de constant	Modernización	Es válido en Solidity 0.4.15. Las versiones posteriores incorporan view.
Ausencia de eventos	Buena práctica	Dificulta el seguimiento de depósitos y retiradas, pero no demuestra una vulnerabilidad de seguridad.
Ausencia de modificadores de visibilidad explícitos	Buena práctica	En Solidity 0.4.15, las funciones sin visibilidad explícita son públicas por defecto. No se identifica un problema de autorización independiente.

4. Limitaciones del análisis
La auditoría se ha realizado exclusivamente sobre el código fuente facilitado.

No se ha verificado:
- La compilación del contrato con una versión concreta del compilador.
- La ejecución de transacciones ni la viabilidad práctica de una secuencia reentrante.
- El saldo real de una instancia desplegada.
- La existencia de otros contratos que interactúen con Reentrance.
- El comportamiento del contrato bajo pruebas dinámicas.
Por tanto, el hallazgo RE-01 está confirmado mediante inspección del código, pero no validado experimentalmente.
5. Conclusión
El contrato Reentrance presenta una vulnerabilidad de reentrancia, clasificada como SWC-107 y de severidad crítica.

La causa principal es la realización de una llamada externa antes de actualizar el saldo interno del usuario.

La mitigación recomendada consiste en aplicar el patrón Checks-Effects-Interactions, modificando el estado antes de efectuar la transferencia de Ether.

No se identifican otras vulnerabilidades independientes suficientemente justificadas a partir del código proporcionado.

Resultado final de la auditoría: 1 hallazgo confirmado por análisis estático, 0 hallazgos adicionales justificados y ninguna prueba dinámica realizada.