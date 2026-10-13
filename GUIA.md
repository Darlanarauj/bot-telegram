# Guia de configuração: Achadinhos no automático

## Como funciona no dia a dia

1. Você acha o produto na Shopee, tira um print limpo da foto (corte só o produto) e gera seu link de afiliado.
2. Manda no **Telegram**, numa conversa privada só sua com o seu bot:
   - **Foto** com a legenda: nome, preço e (se já tiver) o link de afiliado, uma informação por linha.
   - Se ainda não tem o link, manda depois, **respondendo** a mensagem de confirmação do bot.
3. O bot guarda na fila. Duas vezes por dia (12:30 e 20:00) ele pega os próximos produtos, monta o carrossel, escreve a legenda, posta no Instagram e atualiza a página da sua bio.

Exemplo de legenda da foto:

```
Fone Bluetooth TWS
79,90
https://s.shopee.com.br/abc123
```

Comandos no bot: `/fila` mostra a fila, `/apagar` (respondendo a um produto) cancela.

## Parte 1: Telegram (5 minutos)

1. Instale o Telegram e crie sua conta.
2. Procure **@BotFather**, mande `/newbot`, escolha um nome e um usuário terminado em `bot`.
3. Ele devolve um **token**. Guarde, não mostre a ninguém.
4. Abra o seu bot e mande `/start`.

## Parte 2: GitHub (10 minutos)

1. Crie uma conta em github.com e um repositório novo. **Ele precisa ser público**: o GitHub Pages grátis exige isso, e é a página pública que o Instagram usa para buscar as imagens. Suas chaves ficam em "Secrets", que continuam escondidas mesmo com o repositório público.
2. Suba todos os arquivos deste projeto (arrastando as pastas para "Add file > Upload files"). A pasta `.github` precisa ir junto. Se ela não subir, crie os dois arquivos em "Add file > Create new file", digitando o caminho `.github/workflows/postar.yml` e `.github/workflows/receber.yml` e colando o conteúdo.
3. **Settings > Pages > Source: GitHub Actions**.
4. **Settings > Secrets and variables > Actions > New repository secret**. Crie:
   - `TELEGRAM_TOKEN`: o token do BotFather.
   - `TELEGRAM_CHAT_ID`: veja a Parte 3.
   - `GEMINI_API_KEY` (opcional): chave grátis em aistudio.google.com. Sem ela o bot usa uma legenda padrão.
   - `IG_TOKEN`: veja a Parte 4. Só é necessário para postar de verdade.
5. Edite o `config.json`: coloque seu `instagram` (sem @), o título da página e, se quiser, quantos produtos por post.

## Parte 3: descobrir o TELEGRAM_CHAT_ID

1. Com o bot já com `/start` enviado, vá em **Actions > Receber produtos > Run workflow**.
2. O bot responde no Telegram com o seu número de chat. Coloque no segredo `TELEGRAM_CHAT_ID`.
3. Rode "Receber produtos" de novo e mande uma foto de teste. Depois de alguns minutos o bot confirma.

Só o seu chat é aceito. Mensagens de outras pessoas são ignoradas.

## Parte 4: Instagram

Sua conta precisa ser **profissional** (você já é). Não precisa Página do Facebook com este método, mas pode ser que a Meta mude os nomes dos menus. O caminho é:

1. Em developers.facebook.com, crie um app (tipo "Empresa").
2. Adicione o produto/caso de uso da **API do Instagram** com login do Instagram.
3. Adicione sua conta como **testador do Instagram** e aceite o convite no app do Instagram (Configurações > Apps e sites).
4. Gere o **token de acesso** da sua conta com as permissões de publicar conteúdo (`instagram_business_basic` e `instagram_business_content_publish`). Cole no segredo `IG_TOKEN`.
5. O token dura cerca de **60 dias**. Quando os posts falharem com erro de token, gere um novo e atualize o segredo. O GitHub te avisa por e-mail quando o fluxo falha.

Se o bot não achar o ID da sua conta sozinho, crie também o segredo `IG_USER_ID`.

## Parte 5: testar antes de ligar

1. Mande 1 ou 2 produtos de teste para o bot.
2. **Actions > Postar no Instagram > Run workflow** deixando **"Modo teste" marcado**. Ele não posta; no log aparecem a legenda e os endereços das imagens.
3. Abra o endereço da sua página: `https://SEUUSUARIO.github.io/NOMEDOREPOSITORIO/` e confira.
4. Quando estiver tudo certo, rode de novo **desmarcando** "Modo teste" para o primeiro post de verdade.
5. A partir daí os posts saem sozinhos às 12:30 e 20:00 (horário de Brasília). Coloque o endereço da página na **bio do Instagram**.

Para pausar tudo: **Settings > Secrets and variables > Actions > Variables**, crie `PAUSAR` com valor `1`.

## Problemas comuns

- **Nada acontece no Telegram:** o bot só responde quando o fluxo "Receber produtos" roda (a cada ~30 minutos). Para ver na hora, rode manualmente.
- **Fluxo parou de rodar sozinho:** o GitHub desativa agendamentos de repositórios sem atividade por 60 dias. Em Actions, clique para reativar.
- **Erro de imagem ao postar:** o GitHub Pages pode demorar a publicar. O bot espera até 5 minutos. Confira se o Pages está em "GitHub Actions".
- **Preço não aparece no cartão:** mande o preço numa linha só, por exemplo `79,90`.
- **Fila vazia:** o post é pulado sem erro.
