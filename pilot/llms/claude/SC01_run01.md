Informe de auditoría: contrato Reentrance

Alcance: únicamente el código proporcionado. Solidity ^0.4.15. Sin ejecución ni interacción con redes.

Resumen
ID	Categoría	SWC	Severidad	Confianza
F-01	Reentrancy	SWC-107	Crítica	Confirmado por el código
F-02	Overflow aritmético	SWC-101	Baja	Confirmado por el código
F-03	Visibilidad y versión de compilador no fijadas	SWC-100, SWC-103	Informativa	Confirmado por el código
F-01: Reentrancy en withdrawBalance

1. Categoría: Reentrancy (violación del patrón Checks-Effects-Interactions).

2. SWC: SWC-107.

3. Ubicación: withdrawBalance(). La llamada externa msg.sender.call.value(userBalance[msg.sender])() ocurre antes de la instrucción userBalance[msg.sender] = 0;.

4. Causa técnica y condiciones:

call.value(...)() transfiere todo el gas disponible al destinatario y ejecuta su código (fallback) antes de que el saldo se ponga a cero.
Si msg.sender es un contrato, su fallback puede volver a invocar withdrawBalance(). En esa reentrada userBalance[msg.sender] sigue conteniendo el valor original, por lo que el contrato vuelve a enviar esa cantidad.
Condiciones necesarias: (a) el llamante es un contrato con fallback que reentra; (b) tiene saldo > 0 depositado vía addToBalance; (c) el contrato Reentrance mantiene ether de otros usuarios (si solo tuviera el del atacante, no habría pérdida neta ajena).

5. Impacto y severidad: Crítica. Un depositante malicioso puede drenar el ether de otros usuarios depositado en el contrato, hasta agotar su balance o el gas disponible. Se pierden fondos de terceros sin necesidad de privilegios. La severidad se justifica por impacto directo en fondos, explotabilidad sencilla y ausencia de cualquier control compensatorio (no hay mutex, ni propietario, ni pausa).

6. Mitigación: aplicar Checks-Effects-Interactions (poner a cero antes de la llamada externa) y, opcionalmente, un mutex. Compatible con 0.4.15:

solidity
pragma solidity ^0.4.15;

contract Reentrance {
    mapping (address => uint) userBalance;

    function getBalance(address u) constant returns(uint){
        return userBalance[u];
    }

    function addToBalance() payable {
        // Ver F-02: protección contra overflow
        uint newBalance = userBalance[msg.sender] + msg.value;
        require(newBalance >= userBalance[msg.sender]);
        userBalance[msg.sender] = newBalance;
    }

    function withdrawBalance() {
        uint amount = userBalance[msg.sender];
        require(amount > 0);
        userBalance[msg.sender] = 0;          // Effects antes de Interaction
        require(msg.sender.call.value(amount)());  // revierte todo si falla
    }
}

Alternativa más restrictiva: msg.sender.transfer(amount), que limita el gas reenviado a 2300 (reduce la superficie de reentrada, aunque no sustituye al patrón CEI y puede fallar con receptores legítimos cuyo fallback necesite más gas). Con el orden corregido, si la llamada falla el require revierte la puesta a cero, por lo que el usuario no pierde su saldo.

7. Confianza: Confirmado por el código.

F-02: Posible overflow en addToBalance

1. Categoría: Overflow/underflow aritmético.

2. SWC: SWC-101.

3. Ubicación: addToBalance(), línea userBalance[msg.sender] += msg.value;.

4. Causa técnica: En Solidity 0.4.x la aritmética no revierte en overflow (envuelve módulo 2²⁵⁶). Para que ocurra, userBalance[msg.sender] + msg.value tendría que superar 2²⁵⁶−1.

5. Impacto y severidad: Baja. Como msg.value está limitado por el ether realmente existente (muy inferior a 2²⁵⁶ wei), un overflow no es alcanzable en condiciones reales de la red. Se reporta por completitud y por robustez si el código se reutilizara adaptado (p. ej., con tokens o valores arbitrarios).

6. Mitigación: la comprobación require(newBalance >= userBalance[msg.sender]) mostrada en F-01, o una librería SafeMath.

7. Confianza: Confirmado por el código en cuanto a ausencia de la protección; la explotabilidad práctica es muy improbable.

F-03: Buenas prácticas (no son vulnerabilidades explotables)

Se separan de los hallazgos de seguridad:

SWC-100 (visibilidad de funciones no declarada): las funciones no declaran visibilidad. En 0.4.x son public por defecto, lo que coincide con la intención aquí, pero conviene declararlo explícitamente (public). Es un tema de claridad, sin impacto de seguridad en este contrato.
SWC-103 (pragma flotante): ^0.4.15 permite compilar con cualquier 0.4.x ≥ 0.4.15. Recomendable fijar una versión concreta (p. ej. pragma solidity 0.4.26;) para despliegue.
throw y constant: son sintaxis obsoleta (revert()/require() y view en versiones posteriores). view no existe como palabra reservada en 0.4.15, por lo que en esa versión se mantiene constant.
Ausencia de eventos: no se emiten eventos en depósitos ni retiradas. Mejora de trazabilidad, no de seguridad.
Gas: userBalance sin visibilidad explícita; el public generaría un getter redundante con getBalance. Es una decisión de diseño, sin impacto de seguridad.
Observaciones sobre lo no hallado
No se detectan otras vulnerabilidades justificables en el código proporcionado: no hay control de acceso privilegiado, tx.origin, delegatecall, selfdestruct ni dependencia de timestamp.
Limitación: el contrato no tiene función para recuperar ether enviado directamente (sin addToBalance). Si llega ether por selfdestruct de otro contrato, quedará bloqueado. No afecta a la contabilidad de userBalance, y no puede evitarse en el nivel de EVM; es una observación informativa.

Conclusión: el contrato contiene una vulnerabilidad crítica confirmada (reentrancy, F-01), corregible reordenando efectos e interacciones. El resto son riesgos de baja probabilidad o buenas prácticas.