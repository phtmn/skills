/**
 * Google Apps Script Web App - Backend (Código.gs)
 * Desenvolvido seguindo as diretrizes do apps-script-backend.
 */

// Configuração do e-mail de destino.
// Se vazio, enviará para o e-mail do próprio usuário que executa a aplicação.
var EMAIL_DESTINATARIO = "";

/**
 * Renderiza a página Index.html quando o Web App é acessado.
 */
function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
      .setTitle('Formulário de Cadastro')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
      .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/**
 * Função utilitária para incluir arquivos secundários no HTML.
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * Recebe os dados do formulário frontend e processa no servidor.
 * 
 * @param {Object} dados Objeto contendo nome, whatsapp, endereco e foto.
 * @return {Object} Retorna o status e a mensagem de resultado.
 */
function salvarFormulario(dados) {
  try {
    // 1. Validação básica de entrada
    if (!dados.nome || !dados.whatsapp || !dados.endereco) {
      throw new Error("Por favor, preencha todos os campos obrigatórios (Nome, WhatsApp e Endereço).");
    }

    var fileUrl = "Nenhuma foto enviada";

    // 2. Processamento da Foto (Google Drive)
    if (dados.foto && dados.foto.base64) {
      var base64Data = dados.foto.base64;
      // Trata a string base64 se vier no formato Data URL (ex: data:image/png;base64,...)
      if (base64Data.indexOf(",") > -1) {
        base64Data = base64Data.split(",")[1];
      }
      
      var contentType = dados.foto.type || "image/jpeg";
      var filename = dados.foto.name || "foto_" + new Date().getTime() + ".jpg";
      
      // Decodifica a string em bytes e cria um Blob
      var decoded = Utilities.base64Decode(base64Data);
      var blob = Utilities.newBlob(decoded, contentType, filename);
      
      // Verifica/Cria a pasta no Drive
      var folderName = "Formulário Fotos";
      var folders = DriveApp.getFoldersByName(folderName);
      var folder;
      if (folders.hasNext()) {
        folder = folders.next();
      } else {
        folder = DriveApp.createFolder(folderName);
      }
      
      // Cria o arquivo na pasta e ajusta a permissão para visualização via link
      var file = folder.createFile(blob);
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      fileUrl = file.getUrl();
    }

    // 3. Salvamento dos Dados (Google Sheets)
    // Tenta abrir a planilha ativa. Se falhar (ex: executado de forma standalone), 
    // usa a planilha associada ou insere/abre uma planilha padrão.
    var ss;
    try {
      ss = SpreadsheetApp.getActiveSpreadsheet();
      if (!ss) throw new Error("Planilha ativa não encontrada.");
    } catch (e) {
      // Fallback para caso o script seja rodado fora de um Sheet container (como script standalone)
      // Substitua pelo ID da sua planilha caso deseje vincular permanentemente
      throw new Error("Este script precisa ser executado a partir de uma Planilha Google vinculada. Associe este script a um Google Sheet.");
    }

    var sheet = ss.getSheetByName("Respostas");
    if (!sheet) {
      sheet = ss.insertSheet("Respostas");
      // Define cabeçalhos na primeira execução
      sheet.appendRow(["Data/Hora", "Nome Completo", "WhatsApp", "Endereço", "Link da Foto"]);
      sheet.getRange(1, 1, 1, 5).setFontWeight("bold").setBackground("#e0e0e0");
    }

    sheet.appendRow([
      new Date(),
      dados.nome,
      dados.whatsapp,
      dados.endereco,
      fileUrl
    ]);

    // 4. Disparo do E-mail de Notificação (Gmail / MailApp)
    var emailDestino = EMAIL_DESTINATARIO || Session.getActiveUser().getEmail();
    if (!emailDestino) {
      throw new Error("Não foi possível identificar o e-mail de destino. Por favor, configure a variável EMAIL_DESTINATARIO no código.");
    }

    var assunto = "Novo Cadastro Recebido: " + dados.nome;
    
    var htmlContent = "<h2>Novo Formulário de Cadastro</h2>" +
                      "<hr>" +
                      "<p><strong>Nome Completo:</strong> " + dados.nome + "</p>" +
                      "<p><strong>WhatsApp:</strong> " + dados.whatsapp + "</p>" +
                      "<p><strong>Endereço:</strong> " + dados.endereco + "</p>" +
                      "<p><strong>Foto Anexada:</strong> " + 
                      (fileUrl.startsWith("http") ? "<a href='" + fileUrl + "' target='_blank'>Ver Foto no Drive</a>" : fileUrl) + 
                      "</p>" +
                      "<hr>" +
                      "<p style='font-size: 0.8em; color: #777;'>Enviado automaticamente pelo Sistema Google Antigravity.</p>";

    var plainTextContent = "Novo Formulário de Cadastro\n\n" +
                           "Nome Completo: " + dados.nome + "\n" +
                           "WhatsApp: " + dados.whatsapp + "\n" +
                           "Endereço: " + dados.endereco + "\n" +
                           "Foto: " + fileUrl + "\n";

    MailApp.sendEmail({
      to: emailDestino,
      subject: assunto,
      body: plainTextContent,
      htmlBody: htmlContent
    });

    return { 
      status: "success", 
      message: "Seus dados foram salvos com sucesso e a notificação por e-mail foi disparada!" 
    };

  } catch (error) {
    Logger.log("Erro no servidor: " + error.toString());
    return { 
      status: "error", 
      message: "Falha ao processar formulário: " + error.message 
    };
  }
}
