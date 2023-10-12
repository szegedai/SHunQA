<template>
    <div>
        <p v-html="$t('app.description')" class="mb-2"></p>

        <pre class="mb-2 italic">{{ $t('app.exampleQuestion') }}</pre>
        <SearchBar v-model:query="question" :pending="pending" :ask-question="refresh" :error="error" class="mb-4" />
        <AskQuestion v-if="(Object.keys(answer).length == 0 || (Object.keys(answer).length != 0 && pending)) && !error"
            :pending="pending" />
        <Errors v-if="error" :error="error" />
        <AnswerCard :answer="answer" :question="question" :debug="answer.debug" v-if="!pending && answer" />
    </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig().public
const question = ref("")
let answer = ref<any>({})
let pending = ref(false)
let error = ref<any>("")
let refresh = ref()

let data = await useLazyAsyncData("answers", () =>
    $fetch(`${config.apiUrl}/question`,
        {
            method: 'POST',
            body: {
                "query": question.value,
            }
        }
    ).then((res) => {
        error.value = ""
        answer.value = res
    }).catch((err) => {
        error.value = err
        answer.value = {}
    })
)
refresh.value = data.refresh
pending = data.pending
</script>