<template>
    <div>
        <p v-html="$t('app.description')" class="mb-2"></p>

        <pre class="mb-2 italic">{{ $t('app.exampleQuestion') }}</pre>
        <SearchBar v-model:query="question" :pending="pending" :ask-question="refresh" :error="error" class="mb-4" />
        <AskQuestion v-if="Object.keys(answer).length == 0 || (Object.keys(answer).length != 0 && pending)" :pending="pending"/>
        <AnswerCard :answer="answer" :question="question" :debug="answer.debug" v-if="!pending && answer" />

        <!-- {{ answer }} -->
        <!-- {{ pending }} -->
    </div>
</template>

<script setup>
const config = useRuntimeConfig().public
const question = ref("")

// const {
//     data: answer = {},
//     pending = false,
//     error = null,
//     refresh = null
// }
// const answer = ref(null)
// const pending = ref(false)
// const error = ref(null)
// const refresh = ref(null)

const {
    data: answer,
    pending,
    error,
    refresh,
} = await useAsyncData("answers", () =>
    $fetch(`${config.apiUrl}/question`,
        {
            method: 'POST',
            body: {
                "query": question.value,
            }
        }
    )
)

// async function askQuestion() {
//     const {
//         data: answer,
//         pending,
//         error,
//         refresh,
//     } = await useAsyncData("answers", () =>
//         $fetch(`${config.apiUrl}/question`,
//             {
//                 method: 'POST',
//                 body: {
//                     "query": question.value,
//                 }
//             }
//         )
//     )
// }
</script>