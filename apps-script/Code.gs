/**
 * gCite - Google Apps Script Add-on
 * Main code file for Google Docs integration
 */

/**
 * Runs when the add-on is installed or document is opened
 */
function onOpen() {
  DocumentApp.getUi()
    .createMenu('gCite')
    .addItem('Search Citations', 'showSidebar')
    .addItem('Settings', 'showSettings')
    .addToUi();
}

/**
 * Show the search sidebar
 */
function showSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('gCite Search')
    .setWidth(350);
  DocumentApp.getUi().showSidebar(html);
}

/**
 * Show the settings dialog
 */
function showSettings() {
  var html = HtmlService.createHtmlOutputFromFile('Settings')
    .setTitle('gCite Settings')
    .setWidth(400)
    .setHeight(500);
  DocumentApp.getUi().showModalDialog(html, 'gCite Settings');
}

/**
 * Get selected text from the document
 * @return {string} Selected text or empty string
 */
function getSelectedText() {
  var selection = DocumentApp.getActiveDocument().getSelection();
  if (!selection) {
    return '';
  }

  var elements = selection.getRangeElements();
  var text = elements.map(function(element) {
    return element.getElement().asText().getText();
  }).join(' ');

  return text.trim();
}

/**
 * Search citations using the gCite backend API
 * @param {Object} params - Search parameters
 * @return {Object} Search results or error
 */
function searchCitations(params) {
  var apiUrl = getApiUrl();
  var apiKey = getApiKey();

  if (!apiUrl) {
    return {
      error: 'API URL not configured. Please set it in Settings.'
    };
  }

  var payload = {
    query: params.query || '',
    context: params.context || '',
    max_results: params.max_results || 10,
    citation_style: params.citation_style || 'APA',
    filter: params.filter !== undefined ? params.filter : true,
    min_relevance: params.min_relevance || 0.7,
    include_context: params.include_context !== undefined ? params.include_context : true
  };

  var options = {
    method: 'post',
    contentType: 'application/json',
    headers: {},
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  if (apiKey) {
    options.headers['Authorization'] = 'Bearer ' + apiKey;
  }

  try {
    Logger.log('Calling API: ' + apiUrl + '/api/search');
    var response = UrlFetchApp.fetch(apiUrl + '/api/search', options);
    var statusCode = response.getResponseCode();

    if (statusCode !== 200) {
      var errorText = response.getContentText();
      Logger.log('API error ' + statusCode + ': ' + errorText);
      return {
        error: 'API error (' + statusCode + '): ' + errorText
      };
    }

    var data = JSON.parse(response.getContentText());
    Logger.log('API returned ' + data.results_count + ' results');
    return data;

  } catch (error) {
    Logger.log('API call failed: ' + error.toString());
    return {
      error: 'API call failed: ' + error.toString()
    };
  }
}

/**
 * Get API URL from user properties
 * @return {string} API URL
 */
function getApiUrl() {
  var props = PropertiesService.getUserProperties();
  return props.getProperty('GCITE_API_URL') || '';
}

/**
 * Get API key from user properties
 * @return {string} API key
 */
function getApiKey() {
  var props = PropertiesService.getUserProperties();
  return props.getProperty('GCITE_API_KEY') || '';
}

/**
 * Save user preferences
 * @param {Object} prefs - Preferences object
 */
function savePreferences(prefs) {
  var props = PropertiesService.getUserProperties();
  props.setProperties(prefs);
  return { success: true };
}

/**
 * Get user preferences
 * @return {Object} User preferences
 */
function getPreferences() {
  var props = PropertiesService.getUserProperties();
  return {
    GCITE_API_URL: props.getProperty('GCITE_API_URL') || 'http://localhost:8001',
    GCITE_API_KEY: props.getProperty('GCITE_API_KEY') || '',
    citationStyle: props.getProperty('citationStyle') || 'APA',
    maxResults: parseInt(props.getProperty('maxResults')) || 10,
    includeContext: props.getProperty('includeContext') !== 'false',
    minRelevance: parseFloat(props.getProperty('minRelevance')) || 0.7
  };
}
