Auditoría de seguridad: contrato Phishable

Alcance: únicamente el código proporcionado, sin consultas externas. Versión del compilador: pragma solidity ^0.4.22.

Resumen
ID	Categoría	SWC	Severidad	Confianza
H-01	Autorización mediante tx.origin	SWC-115	Alta	Confirmado por el código
H-02	Constructor sin visibilidad explícita (pragma ^0.4.22)	SWC-118 (relacionado)	Informativa	Confirmado, impacto bajo

El resto de observaciones son recomendaciones de buenas prácticas, separadas al final.

H-01: Autorización con tx.origin (vulnerable a phishing por contrato intermediario)

1. Categoría: Control de acceso defectuoso / uso de tx.origin para autorización.

2. SWC: SWC-115 (Authorization through tx.origin).

3. Ubicación: función withdrawAll(address _recipient), instrucción require(tx.origin == owner); (la línea inmediatamente posterior a la declaración de la función).

4. Causa técnica y condiciones:
tx.origin es la EOA que firmó la transacción original, no el emisor inmediato de la llamada (msg.sender). La comprobación valida quién inició la cadena de llamadas, no quién invoca directamente la función.

Condiciones necesarias:

El owner debe ser una EOA (si fuera un contrato, tx.origin nunca podría igualarlo y la función quedaría inutilizable, véase la nota en H-01b).
El contrato debe tener saldo.
El owner debe ser inducido a enviar una transacción (firmada por él) a un contrato controlado por un tercero, por ejemplo mediante ingeniería social, un token o dApp falsa, o el envío de ether a una dirección que ejecute código en su función de recepción. Ese contrato intermediario puede entonces llamar a Phishable.withdrawAll(atacante) en la misma transacción; como tx.origin == owner, la comprobación pasa.
Nada en el contrato exige que _recipient guarde relación con el owner: el destino lo elige el llamante.

5. Impacto y severidad: Pérdida total del saldo del contrato en una sola transacción. El requisito de interacción del propietario con un contrato malicioso reduce la probabilidad, pero no la gravedad del impacto, que es la pérdida completa de fondos. Severidad: Alta. El diseño es el patrón clásico documentado como erróneo, y la mitigación es trivial.

6. Mitigación: usar msg.sender en lugar de tx.origin.

solidity
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
        require(_recipient != address(0));
        _recipient.transfer(address(this).balance);
    }
}

Notas sobre el código corregido:

msg.sender == owner obliga a que el propietario llame directamente, por lo que un contrato intermediario no puede suplantarlo.
address(this).balance sustituye a this.balance, que está deprecado desde 0.4.21 (genera advertencia) y se elimina en 0.5.0. Ambas formas son válidas en ^0.4.22.
Si owner pudiera ser un contrato (multisig), msg.sender también funcionaría, mientras que tx.origin lo impediría.

7. Confianza: Confirmado por el código. La comprobación sobre tx.origin es evidente y no depende de código ajeno. La explotación depende de un factor externo (que el propietario interactúe con un contrato malicioso), pero la debilidad en sí está demostrada.

H-02: Constructor sin visibilidad explícita (informativo)

1. Categoría: Visibilidad / compatibilidad entre versiones del compilador.

2. SWC: SWC-118 está definido para nombres de constructor incorrectos (constructores antiguos); aquí no aplica estrictamente, pero es el hallazgo más próximo. Lo trato como observación sin SWC directo.

3. Ubicación: constructor (address _owner).

4. Causa técnica: En Solidity 0.4.x un constructor sin visibilidad es public por defecto. Desde 0.7.0 la visibilidad del constructor se ignora y su especificación genera advertencia. Con ^0.4.22 el código compila y se comporta correctamente.

5. Impacto: Ninguno en seguridad para este contrato. El comportamiento es el esperado (el constructor solo se ejecuta en el despliegue). Severidad: Informativa.

6. Mitigación: declarar public explícitamente (ya incluido en el código de H-01), lo que además evita la advertencia del compilador.

7. Confianza: Confirmado, sin impacto de seguridad.

Observaciones adicionales (no son vulnerabilidades)

Seguridad menor / robustez (recomendaciones):

Sin validación de _owner en el constructor: si se despliega con address(0), los fondos quedarían bloqueados. Incluido require en la corrección.
Sin validación de _recipient: enviar a address(0) quemaría los fondos. Es un error de usuario, no una vulnerabilidad externa.
Sin mecanismo de transferencia de propiedad: si la clave del propietario se pierde o se compromete, no hay recuperación. Decisión de diseño; valorar un patrón Ownable.
Uso de transfer: reenvía solo 2300 de gas. Si _recipient es un contrato cuya función de recepción necesita más, la retirada revertirá. No es un fallo de seguridad, sino una limitación de funcionalidad; en 0.4.x la alternativa es call.value(...)(), que reintroduciría riesgo de reentrada y debería usarse con cuidado.
Función de respaldo payable sin eventos: no se emite ningún evento en depósitos ni retiradas, lo que dificulta la monitorización. Recomendación de buenas prácticas (por ejemplo event Withdrawn(address indexed to, uint256 amount)).

Estilo / gas:

La función withdrawAll podría declararse external (en 0.4.x hay ahorro de gas marginal en algunos casos).
Falta documentación NatSpec.
Aspectos analizados sin hallazgo
Reentrada (SWC-107): withdrawAll solo realiza un transfer (2300 de gas) y no modifica estado después, por lo que no hay vector de reentrada explotable.
Desbordamiento aritmético (SWC-101): no hay aritmética en el contrato.
Self-destruct / delegatecall: ausentes.
Ether forzado: el saldo puede aumentar por selfdestruct ajeno, pero no afecta a la lógica, ya que withdrawAll transfiere el saldo completo.
Conclusión

El contrato presenta una vulnerabilidad real de severidad alta (H-01): la autorización basada en tx.origin permite el robo completo de fondos si el propietario es inducido a interactuar con un contrato malicioso. La corrección consiste en usar msg.sender. No he detectado otras vulnerabilidades justificables en el código proporcionado.