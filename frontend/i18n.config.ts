export default defineI18nConfig(() => ({
  legacy: false,
  locale: "hu",
  warnHtmlInMessage: "off",
  messages: {
    hu: {
      app: {
        title: 'Projectroom<span class="text-lime-600">41</span>: <span class="font-medium">SHunQA</span>',
        description: '',
        exampleQuestion: 'Mikor építették a vízlépcsőket a Duna felső szakaszán?',
        questionPlaceholder: 'Mi a kérdésed?',
        context: 'Dokumentumrészlet',
        source: 'Forrás',
        loading: 'Töltés...',
        feedback: {
          like: 'Tetszik ez a válasz',
          dislike: 'Nem tetszik ez a válasz',
          toast: {
            success: 'Köszönjük a visszajelzést!',
            error: 'Hiba történt a visszajelzés elküldése közben. Próbáld újra később!',
          },
          modal: {
            close: 'Bezárás',
            title: 'Valami nem helyes?',
            subtitle: 'Írj egy visszajelzést!',
            whatShouldBe: 'Mi lett volna a helyes válasz?',
            whatsWrong: 'Mi a probléma ezzel a válasszal?',
            wasThisInTheContext: 'A helyes válasz benne volt a dokumentumrészletben?',
            yes: 'Igen',
            no: 'Nem',
            notSure: 'Nem vagyok biztos benne',
            anythingElse: 'Szeretnél még bármit hozzátenni ehhez a visszajelzéshez?',
            send: 'Küldés',
          }
        },
      },
      l10n: {
        quoteStart: '„',
        quoteEnd: '”',
      },
      debug: {
        settings: 'Hibakeresési beállítások',
        modelScore: 'Modell pontszám',
        elasticScore: 'Elastic pontszám',
      },
    },
    en: {
      app: {
        title: 'Projectroom<span class="text-lime-600">41</span>: <span class="font-medium">SHunQA</span>',
        description: '',
        exampleQuestion: 'Mikor építették a vízlépcsőket a Duna felső szakaszán?',
        questionPlaceholder: 'What is your question?',
        context: 'Context',
        source: 'Source',
        loading: 'Loading...',
        feedback: {
          like: 'I like this answer',
          dislike: 'I don\'t like this answer',
          toast: {
            success: 'Thanks for the feedback!',
            error: 'An error occurred while sending the feedback. Please try again later!',
          },
          modal: {
            close: 'Close',
            title: 'Something not right?',
            subtitle: 'Leave a feedback!',
            whatShouldBe: 'What should be the correct answer?',
            whatsWrong: 'What is wrong with this answer?',
            wasThisInTheContext: 'Was the correct answer in the context?',
            yes: 'Yes',
            no: 'No',
            notSure: 'Not sure',
            anythingElse: 'Anything else would you want to add to the feedback?',
            send: 'Send',
          }
        },
      },
      l10n: {
        quoteStart: '„',
        quoteEnd: '”',
      },
      debug: {
        settings: 'Debug settings',
        modelScore: 'Model score',
        elasticScore: 'Elastic score',
      },
    },
  },
}));
