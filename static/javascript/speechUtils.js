const synth = window.speechSynthesis;
const LS = localStorage;
export function speak(data) {
const text = typeof data === 'string' ? data : data.inputTxt; // Adjust to get text from data
let formData  = {};

if (LS.getItem('formData')){
    formData = JSON.parse(localStorage.getItem('formData'));
}
else{
    formData["pitch"] = 1;
    formData["rate"] = 1;
    formData["voice"] = "Google русский";
    LS.setItem('formData', JSON.stringify(formData))
}
// Pass the text as a parameter
  if (synth.speaking) {
    console.error('speechSynthesis.speaking');
    synth.cancel();
    setTimeout(() => speak(text), 300); // Pass the text again when retrying
  } else if (text !== '') { // Use the text parameter here
    const utterThis = new SpeechSynthesisUtterance(text); // Use text parameter
    console.log(utterThis)
    utterThis.onend = function(event) {
      console.log('SpeechSynthesisUtterance.onend');
    };
    utterThis.onerror = function(event) {
      console.error('SpeechSynthesisUtterance.onerror');
    };
    let selectedOption; // Declare selectedOption outside the if block
    if (formData["voice"]) {
      selectedOption = formData["voice"];
    } else {
      selectedOption = "Google русский";
    }
    utterThis.onpause = function(event) {
      const char = event.utterance.text.charAt(event.charIndex);
      console.log(
        'Speech paused at character ' +
          event.charIndex +
          ' of "' +
          event.utterance.text +
          '", which is "' +
          char +
          '".'
      );
    };

    if (formData["pitch"]) {
      utterThis.pitch = formData["pitch"];
    } else {
      utterThis.pitch = 1;
    }
    if (formData["rate"]) {
      utterThis.rate = formData["rate"];
    } else {
      utterThis.rate = 1;
    }
    utterThis.lang = "Google русский";
    synth.speak(utterThis);
  }
}

// ... (remaining code)
