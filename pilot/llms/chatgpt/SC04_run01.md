Auditoría de seguridad del contrato Phishable
Resultado del análisis estático
1 vulnerabilidad crítica

1
Crítica

0
Media / Baja

1
Total



Alcance: análisis exclusivamente del código Solidity proporcionado, sin ejecución, herramientas externas ni comprobación de despliegues.

Versión: Solidity ^0.4.22 (desde 0.4.22 hasta antes de 0.5.0).
H-01 — Autenticación insegura mediante tx.origin
Campo	Resultado
Identificador	H-01
Categoría	Autenticación y control de acceso
SWC	SWC-115 — Authorization through tx.origin
Severidad	Crítica
Función afectada	withdrawAll(address _recipient)
Instrucción vulnerable	require(tx.origin == owner);
Confianza	Confirmado por el código

1. Descripción técnica
La función withdrawAll() utiliza tx.origin para verificar que la transacción ha sido iniciada por el propietario del contrato.
function withdrawAll(address _recipient) public {
    require(tx.origin == owner);
    _recipient.transfer(this.balance);
}


El problema es que tx.origin representa la cuenta externa que originó la transacción, no necesariamente la cuenta que está llamando directamente a Phishable.

Por tanto, si el propietario inicia una transacción hacia un contrato intermediario y este invoca withdrawAll(), la comprobación seguirá siendo válida.

El contrato tampoco exige que _recipient coincida con owner, por lo que el destino de los fondos puede ser elegido por el intermediario.
2. Condiciones necesarias
Para que se produzca una explotación deben cumplirse las siguientes condiciones:
1. El propietario debe ser una cuenta externa capaz de originar la transacción.
2. El propietario debe iniciar una transacción que provoque una llamada indirecta a Phishable.withdrawAll().
3. El contrato intermediario debe realizar dicha llamada y especificar una dirección receptora.
4. El contrato Phishable debe disponer de saldo para que exista una pérdida económica.
Estas condiciones no demuestran que haya ocurrido un ataque, pero el código permite ese escenario.
3. Impacto potencial
Un contrato intermediario malicioso podría provocar la transferencia de todo el saldo de Phishable a una dirección seleccionada por él, siempre que consiga que el propietario origine la transacción correspondiente.

Severidad: Crítica. La vulnerabilidad afecta directamente al control de acceso de una operación que transfiere la totalidad de los fondos. Su explotación puede causar la pérdida completa del saldo, aunque requiere la participación del propietario mediante una transacción iniciada por este.
4. Mitigación
Debe utilizarse msg.sender para comprobar la identidad del llamante inmediato, en lugar de tx.origin.

Fragmento corregido, compatible con Solidity 0.4.22:
function withdrawAll(address _recipient) public {
    require(msg.sender == owner);
    _recipient.transfer(address(this).balance);
}


Con este cambio, una llamada realizada por un contrato intermediario no superará la autorización cuando owner sea la cuenta externa que originó la transacción.

La corrección presupone que el propietario autorizado debe llamar directamente a la función. Si se requiere un propietario que sea otro contrato, será necesario diseñar el mecanismo de autorización conforme a ese requisito.

Confianza: Confirmado por el código. El uso de tx.origin como mecanismo de autorización es directamente observable. La explotación efectiva depende de las condiciones descritas.

Observaciones adicionales no clasificadas como vulnerabilidades
Elemento	Evaluación
constructor(address _owner)	No valida que _owner sea distinto de address(0). Puede provocar pérdida de acceso a withdrawAll(), pero no se puede determinar si es una vulnerabilidad explotable sin conocer el proceso de despliegue.
_recipient.transfer(...)	Puede revertir si el destinatario rechaza Ether o necesita más gas del proporcionado por transfer. No se demuestra una denegación de servicio explotable por un tercero en este contrato.
function () public payable {}	Permite recibir Ether. No constituye por sí misma una vulnerabilidad.
this.balance	Sintaxis válida en Solidity 0.4.x. Puede sustituirse por address(this).balance para mejorar la claridad.
Ausencia de eventos	Podrían añadirse eventos para registrar retiradas, pero se trata de una mejora de observabilidad, no de una vulnerabilidad demostrada.

Contrato corregido completo
pragma solidity ^0.4.22;

contract Phishable {
    address public owner;

    constructor(address _owner) public {
        require(_owner != address(0));
        owner = _owner;
    }

    function () public payable {}

    function withdrawAll(address _recipient) public {
        require(msg.sender == owner);
        _recipient.transfer(address(this).balance);
    }
}


La validación de _owner es una medida preventiva adicional. El cambio que corrige la vulnerabilidad H-01 es la sustitución de tx.origin por msg.sender.
Conclusión de la auditoría
Se identifica una vulnerabilidad de seguridad justificada, clasificada como SWC-115, causada por utilizar tx.origin para autorizar la retirada de fondos.

La vulnerabilidad permite que un contrato intermediario eluda la intención del control de acceso cuando el propietario inicia la transacción, pudiendo ocasionar la transferencia de todo el saldo a un destinatario no autorizado.

No se identifican otras vulnerabilidades explotables que puedan justificarse exclusivamente con el código proporcionado.

Limitación: las conclusiones proceden de una revisión estática manual. No se han realizado pruebas dinámicas, análisis de bytecode ni validación de condiciones reales de explotación.