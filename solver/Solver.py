import pulp
import dados


N_MODULOS = 1000

AREA = {}
for c, v in dados.area_lavoura().items():
    AREA[dados.MUNICIPIOS[c]] = v

ARM_E = {}
for c, v in dados.armazenagem().items():
    ARM_E[dados.MUNICIPIOS[c]] = v

    

TAM = sum(AREA.values()) / N_MODULOS

