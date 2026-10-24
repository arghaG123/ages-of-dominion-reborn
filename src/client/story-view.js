// Story screen copy. Chapter N opens when the age index is at least N.
// The Valley We Keep is shown only after every chapter choice is stored.
// Acknowledging it grants nothing; reaching the Future age does not skip the choices.
import { futureConclusion } from '../core/campaign.js';

export function storyScreen(state, data) {
  const chapterIndex = state?.story?.chapter ?? 0;
  const chapter = data.STORY[chapterIndex] || null;
  const chapterOpen = Boolean(chapter) && state.age >= chapterIndex;
  const choicesStored = chapterIndex >= data.STORY.length;
  const keepValley = state.age >= 7 && choicesStored && !state.story.futureSeen;
  const concluded = Boolean(state.story.futureSeen) && choicesStored;
  let text;
  if (chapterOpen) text = `${chapter.t}. ${chapter.d}`;
  else if (state.age >= 7 && choicesStored) text = futureConclusion(state, data);
  else if (chapter) text = `${chapter.t} opens in ${data.AGES[chapterIndex].n}. Each chapter opens with its age and pays once. The Valley We Keep opens in the Future age and grants nothing.`;
  else text = 'Each chapter opens with its age and pays once. The Valley We Keep opens in the Future age and grants nothing.';
  return {
    title: chapterOpen ? chapter.t : (concluded || (state.age >= 7 && choicesStored) ? 'The Valley We Keep' : (chapter?.t || 'Story')),
    text,
    choices: chapterOpen ? chapter.ch.map(choice => choice.t) : [],
    keepValley,
    concluded,
  };
}

export function storyHeaderTitle(state, data) {
  const screen = storyScreen(state, data);
  const total = data.STORY.length + 1;
  const chapter = Number.isInteger(state?.story?.chapter) ? state.story.chapter : 0;
  const progress = Math.min(total, Math.max(1, chapter + 1));
  return `${screen.title} (${progress}/${total})`;
}

// The Story chamber paints this. The panel message is not the screen.
// Future age alone stays closed. Keep the valley shows futureConclusion.
export function storyChamberLine(state, data) {
  const screen = storyScreen(state, data);
  if (screen.concluded || screen.keepValley) {
    return { conclusion: screen.concluded ? 'kept' : 'open', text: screen.text };
  }
  return {
    conclusion: 'closed',
    text: 'The Valley We Keep opens after every chapter choice. Reaching the Future age does not skip those choices.',
  };
}
