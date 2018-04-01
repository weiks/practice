const SpeechRecognition = webkitSpeechRecognition;
const SpeechGrammarList = webkitSpeechGrammarList;
const SpeechRecognitionEvent = webkitSpeechRecognitionEvent;

/**
 * you can define your own grammar list
 */
const commands = [ 'play', 'next', 'repeat', 'stop', 'pause' ];
const grammar = '#JSGF V1.0; grammar commands; public <color> = ' + commands.join(' | ') + ' ;';

const recognition = new SpeechRecognition();
const speechRecognitionList = new SpeechGrammarList();

/**
 *  add grammars
 *  the second parameter is a weight value that specifies the importance of this grammar 
 *  in relation of other grammars available in the list (can be from 0 to 1 inclusive.)
 */
speechRecognitionList.addFromString(grammar, 1);
recognition.grammars = speechRecognitionList;

/**
 * other settings
 */
recognition.lang = 'en-US';
recognition.continuous = true;
recognition.interimResults = false;
recognition.maxAlternatives = 1;

/**
 * event handlers
 */
recognition.onresult = (e) => {
  const result = e.results[e.results.length - 1][0].transcript;
  console.log('result: ', result);
  updateResult(result);
}

recognition.onerror = (e) => {
  console.error(e);
}

recognition.onend = () => {
  console.log('recognition end.');
}

/**
 * other functions
 */
function updateResult(result) {
  document.querySelector('#recognitionResult').innerHTML = result;
  if (result==='stop'){
    console.log("STOP!")
    player.stopVideo()
  }
}

function start() {
  recognition.start();
}