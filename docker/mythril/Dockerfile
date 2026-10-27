FROM mythril/myth@sha256:49e11758e359d0b410f648df5bbcba28a52e091a78e4772b5c02b9043666b4ff

# Permisos para modificar la dependencia
USER root

# Corregir el dominio obsoleto de py-solc-x 1.1.1
RUN python -c "import solcx.install as s; \
p=s.__file__; \
data=open(p).read(); \
old='solc-bin.ethereum.org'; \
new='binaries.soliditylang.org'; \
assert old in data, 'Dominio antiguo no encontrado'; \
open(p,'w').write(data.replace(old,new))"

# Recuperar el usuario original de Mythril
USER mythril
