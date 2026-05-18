# Contribuindo para o RevLabs

Primeiramente, obrigado por considerar contribuir para o RevLabs! Seja reportando um bug, propondo um novo recurso ou enviando um pull request, sua ajuda é muito apreciada.

Este documento descreve as diretrizes e etapas para contribuir com o projeto.

---

## 1. Código de Conduta

Ao participar deste projeto, você concorda em seguir as diretrizes padrão da comunidade de código aberto. Por favor, seja acolhedor, inclusivo e respeitoso com todos os contribuidores. Assédio ou comportamento discriminatório não serão tolerados.

---

## 2. Primeiros Passos (Desenvolvimento Local)

O RevLabs é construído com Django. Para configurar e executar seu ambiente de desenvolvimento local, siga estas etapas:

### Pré-requisitos
* Python 3.14+
* Git

### Etapas de Configuração

**1. Faça um Fork e Clone o Repositório**  
Faça um fork do repositório para sua própria conta do GitHub e clone-o em sua máquina local:

```bash
git clone https://github.com/ArthurVFT/RevLabs.git

cd RevLabs
```

**2. Crie um Ambiente Virtual**  
É altamente recomendável usar um ambiente virtual para gerenciar as dependências:

```bash
python -m venv .venv

# No macOS/Linux
source .venv/bin/activate

# No Windows
.venv\Scripts\activate
```

**3. Instale as Dependências**  
Instale os pacotes Python necessários do requirements.txt:

```bash
pip install -r requirements.txt
```

**4. Configure o Banco de Dados**  
Aplique as migrações do Django para configurar seu banco de dados SQLite local:

```bash
python manage.py migrate
```
**5. Preencha os Dados Iniciais**  
O RevLabs depende de peças, carros e pistas predefinidos. Execute o script de população para semear seu banco de dados local:

```bash
python populateparts.py
```

**6. Execute o Servidor de Desenvolvimento**  
Inicie o servidor de desenvolvimento do Django:

```bash
python manage.py runserver
```

Você pode agora acessar a aplicação em http://127.0.0.1:8000/.

---

## 3. Como Contribuir

**Reportando Bugs**  
Se você encontrar um bug, por favor, abra uma issue no GitHub. Inclua:

- Um título claro e descritivo.

- Passos para reproduzir o bug

- Comportamento esperado vs. comportamento real.

- Detalhes sobre seu ambiente (SO, Navegador, versão do Python).

**Sugerindo Melhorias**     
Tem uma ideia para um novo recurso?

- Abra uma issue usando o rótulo "Enhancement" (Melhoria).

- Explique por que esse recurso seria útil e como ele deve funcionar.

**Enviando Pull Requests**  
Agradecemos pull requests para correções de bugs e novos recursos!

1. **Crie uma nova branch:** Sempre crie a partir da main para o seu trabalho.
```bash
git checkout -b feature/your-feature-name
```
2. **Faça suas alterações:** Escreva seu código, garantindo que ele siga as diretrizes de estilo do projeto.

3. **Faça o commit de suas alterações:** Use mensagens de commit claras e descritivas.

4. **Teste seu código:** Execute os testes existentes e adicione novos se necessário (veja a seção de Testes abaixo).

5. **Faça o push e abra um PR:** Faça o push de sua branch para o seu fork e envie um Pull Request. Forneça um resumo claro de suas alterações na descrição do PR.

---

## 4. Diretrizes de Codificação

-  **Python:** Siga as diretrizes padrão [PEP 8](https://pep8.org/) para código Python.

- **Django:** Siga as convenções padrão do Django para models, views e templates.

- **Static Assets:** Coloque novas imagens, CSS ou JS nas pastas categorizadas apropriadamente em revlabs/static/ (ex., img/cars/, img/mods/, css/).

---

## 5. Testes

Antes de enviar um pull request, certifique-se de que suas alterações não quebrem a funcionalidade existente. O RevLabs usa testes padrão do Django, bem como Selenium para testes de UI.

Para rodar os testes com Selenium:
```bash
python revlabs/tests_selenium.py
```

Para rodar os testes padrão do Django:
```bash
python manage.py test
```

(Nota: Se você estiver adicionando novos recursos de UI, por favor considere adicionar testes Selenium correspondentes!)

---

Novamente, obrigado por suas contribuições e por ajudar a tornar o RevLabs melhor!