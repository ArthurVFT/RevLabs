from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# -------------------------------------------------------------------------
# Configuração base extraída do guia
# -------------------------------------------------------------------------
class BaseTestCase(LiveServerTestCase):
    """
    Classe-base que inicializa e encerra o Chrome em modo headless
    (sem interface gráfica) antes e depois de cada teste[cite: 31, 32].
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        # Para rodar no GitHub Actions (CI/CD), descomente a linha abaixo[cite: 260]:
        # opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,800")

        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=opts)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
        super().tearDownClass()

    def abrir_pagina(self, caminho="/"):
        """Navega para uma URL relativa ao servidor de teste[cite: 62]."""
        self.driver.get(self.live_server_url + caminho)


# -------------------------------------------------------------------------
# Testes End-to-End do RevLabs
# -------------------------------------------------------------------------
class Teste_01_FluxoSimulador(BaseTestCase):
    """Testa o fluxo principal do simulador RevLabs: Pistas -> Carros -> Dashboard."""

    def test_01_deve_carregar_selecao_de_pistas(self):
        print("Teste 01: Visualização da página de seleção de pistas.")
        
        # Abre a página inicial de pistas
        self.abrir_pagina("/")
        
        body = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verifica se o título e uma das pistas estão na página
        self.assertIn("Select your Circuit", body.text)
        self.assertIn("Interlagos - Brazil", body.text)
        
        time.sleep(2)  # Apenas para visualizar o teste [cite: 103]

    def test_02_deve_navegar_para_selecao_de_carros(self):
        print("Teste 02: Navegação da seleção de pistas para seleção de carros.")
        self.abrir_pagina("/")
        
        # Clica no card da pista de Interlagos
        link_interlagos = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//h3[text()='Interlagos - Brazil']/ancestor::a"))
        )
        link_interlagos.click()
        
        body = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verifica se navegou para a página de veículos
        self.assertIn("Top Choices", body.text)
        self.assertIn("Mercedes-AMG GT Black Series", body.text)
        
        time.sleep(2)

    def test_03_deve_navegar_para_dashboard_e_ver_tempo(self):
        print("Teste 03: Navegação para o dashboard e visualização do tempo de volta.")
        
        # Navega para a seleção de carros com a pista setada na URL
        self.abrir_pagina("/vehicles/?track=interlagos")
        
        # Clica no card do VW Fusca
        link_carro = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'car-name') and text()='VW Fusca']/ancestor::a"))
        )
        link_carro.click()
        
        body = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verifica se as informações de dashboard renderizaram corretamente
        self.assertIn("Lap time on this track", body.text)
        self.assertIn("VW Fusca", body.text)
        self.assertIn("Interlagos - Brazil", body.text)
        
        time.sleep(2)

    def test_04_deve_interagir_com_menu_de_mods(self):
        print("Teste 04: Interação com os MODs e cálculo de tempo no dashboard.")
        
        # Navega direto para o dashboard do Fusca em Interlagos
        self.abrir_pagina("/dashboard/?track=interlagos&car=fusca")
        
        # Abre o menu clicando no slot MOD 1
        mod_slot = self.wait.until(
            EC.element_to_be_clickable((By.ID, "mod-1"))
        )
        mod_slot.click()
        
        # Aguarda o menu dropdown de mods aparecer
        menu = self.wait.until(
            EC.visibility_of_element_located((By.ID, "mod-dropdown"))
        )
        self.assertTrue(menu.is_displayed())
        
        time.sleep(1)
        
        # Instala a parte 'Medium - RPM Turbocharger' (reduz 4% do tempo)
        turbo_option = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Medium - RPM Turbocharger']/ancestor::div[contains(@class, 'part-item')]"))
        )
        turbo_option.click()
        
        # O Fusca tem tempo base de 2:30.000 (150 segundos). 
        # Com redução de 4%, o tempo cai para 144 segundos, ou seja, 2:24.000.
        time_display = self.wait.until(
            EC.presence_of_element_located((By.ID, "lap-time-display"))
        )
        
        time.sleep(2)
        
        # Verifica se o JS na tela processou o novo tempo com a melhoria
        self.assertIn("2:24.000", time_display.text)