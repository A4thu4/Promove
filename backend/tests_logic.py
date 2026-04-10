import unittest
from datetime import date
from backend.app.core.logic import calcular_carreira, validar_evolucao

class TestLogic(unittest.TestCase):
    def test_basic_evolution_promove(self):
        # Caso simples: Servidor Promove, nível A, sem afastamentos, com 18 meses
        data_inicial = date(2022, 1, 1)
        carreira = calcular_carreira(is_ueg=False, data_enquadramento=date(2022, 1, 1), data_inicial=data_inicial,
                                     pts_ultima_evolucao=0.0, afastamentos=[],
                                     aperfeicoamentos=[(date(2022, 2, 1), 10.0)], titulacoes=[], resp_unicas=[],
                                     resp_mensais=[], dados_tit={})
        
        # Em 18 meses, ele ganha:
        # Efetivo: 18 * 0.2 = 3.6
        # Desempenho: 18 * 1.5 = 27
        # Aperfeiçoamento: 0.9
        # Total: 31.5 (Não atinge 48)
        
        result = validar_evolucao(False, "A", carreira, data_inicial)
        print(f"\nResultado test_basic_evolution_promove: {result}")
        self.assertEqual(result["Status"], "Não apto a evolução")
        self.assertIn("aperfeiçoamento insuficiente", result["Observação"])

    def test_evolution_with_resp_mensal(self):
        data_inicial = date(2022, 1, 1)
        # 12 meses de DAS1 (1.0 pts/mês)
        resp_mensais = [("C. Comissão: DAS1", date(2022, 1, 1), date(2022, 12, 31), 1.0)]
        
        carreira = calcular_carreira(is_ueg=False, data_enquadramento=date(2022, 1, 1), data_inicial=data_inicial,
                                     pts_ultima_evolucao=0.0, afastamentos=[],
                                     aperfeicoamentos=[(date(2022, 1, 1), 100.0)], titulacoes=[], resp_unicas=[],
                                     resp_mensais=resp_mensais, dados_tit={})
        
        # Em 18 meses:
        # Efetivo: 3.6
        # Desempenho: 27
        # Aperfeiçoamento: 9
        # Resp Mensal: 12 * 1.0 = 12
        # Total: 51.6 (Atinge 48)
        
        result = validar_evolucao(False, "A", carreira, data_inicial, True)
        print(f"\nResultado test_evolution_with_resp_mensal: {result}")
        self.assertEqual(result["Status"], "Apto a evolução")
        self.assertEqual(result["Próximo Nível"], "B")

    def test_evolution_ueg(self):
        data_inicial = date(2022, 1, 1)
        # Na UEG, o desempenho é 1.8 por mês.
        # Em 18 meses: 18 * 1.8 = 32.4
        # Efetivo: 18 * 0.2 = 3.6
        # Total: 36.0 (Não atinge 48)
        # Ele atingirá 48 pontos em 24 meses (24 * 2.0 = 48)
        
        carreira = calcular_carreira(is_ueg=True, data_enquadramento=date(2022, 1, 1), data_inicial=data_inicial,
                                     pts_ultima_evolucao=0.0, afastamentos=[], aperfeicoamentos=[], titulacoes=[],
                                     resp_unicas=[], resp_mensais=[], dados_tit={})
        result = validar_evolucao(True, "A", carreira, data_inicial)
        print(f"\nResultado test_evolution_ueg (Sem DAS): {result}")
        
        # Ele deve estar apto, mas na data correta (24 meses depois)
        self.assertEqual(result["Status"], "Apto a evolução")
        self.assertEqual(result["Data da Pontuação Atingida"], "01/01/2024")
        self.assertEqual(result["Interstício de Evolução"], 24)

        # Com 25 meses de DAS1 (1.0 pts/mês)
        # 36.0 + 25 = 61.0 (Atinge 48)
        resp_mensais = [("C. Comissão: DAS1", date(2020, 1, 1), date(2024, 1, 1), 1.0)]
        carreira_ok = calcular_carreira(is_ueg=True, data_enquadramento=date(2022, 1, 1), data_inicial=data_inicial,
                                        pts_ultima_evolucao=0.0, afastamentos=[], aperfeicoamentos=[], titulacoes=[],
                                        resp_unicas=[], resp_mensais=resp_mensais, dados_tit={})
        result_ok = validar_evolucao(True, "A", carreira_ok, data_inicial)
        print(f"Resultado test_evolution_ueg (Com DAS): {result_ok}")
        self.assertEqual(result_ok["Status"], "Apto a evolução")

if __name__ == '__main__':
    unittest.main()
