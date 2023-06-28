<template>
    <div>
        <div v-if="open" class="rounded-md bg-slate-200 my-4 p-4 border border-gray-300 flex flex-col space-y-2">
            <input type="number" v-model="settings.size" class="w-16 rounded-md border border-gray-300 p-1" />
            <select v-model="settings.elastic" class="rounded-md border border-gray-300 p-1 bg-white">
                <option value="milqa_w_lemma_w_official_context">milqa_w_lemma_w_official_context</option>
                <option value="word_war_2_wikidump">word_war_2_wikidump</option>
            </select>
            <select v-model="settings.model_type" class="rounded-md border border-gray-300 p-1 bg-white">
                <!-- <option value="ZTamas/hubert-qa-milqa">ZTamas/hubert-qa-milqa</option>
                <option value="ZTamas/hubert-qa-milqa-impossible">ZTamas/hubert-qa-milqa-impossible</option>
                <option value="ZTamas/hubert-qa-milqa-impossible-long-answer">ZTamas/hubert-qa-milqa-impossible-long-answer
                </option>
                <option value="ZTamas/xlm-roberta-large-squad2-qa-milqa-impossible">
                    ZTamas/xlm-roberta-large-squad2-qa-milqa-impossible</option> -->
                <option value="ZTamas/xlm-roberta-large-squad2_impossible_long_answer">
                    ZTamas/xlm-roberta-large-squad2_impossible_long_answer</option>
            </select>
        </div>

        <pre class="mb-2 italic">Mikor építették a vízlépcsőket a Duna felső szakaszán?</pre>
        <SearchBar v-model:query="question" :pending="pending" :ask-question="askQuestion" :error="error" />
        <p v-if="!pending && answers" v-for="answer in answers.answers">
            <AnswerCard :answer="answer" :question="question" :system="answers.system" />
        </p>
    </div>
</template>

<script setup>
defineProps({
    open: Boolean
})

const question = ref("")
const settings = ref({
    size: 1,
    elastic: "milqa_w_lemma_w_official_context",
    model_type: "ZTamas/xlm-roberta-large-squad2_impossible_long_answer"
})
const config = useRuntimeConfig().public

const {
    data: answers,
    pending,
    error,
    refresh
} = useAsyncData("answers", () => $fetch(`${config.apiUrl}/qa`,
    // } = useAsyncData("answers", () => $fetch(`/api/qa`,
    {
        method: 'POST',
        body: {
            "query": question.value,
            "size": settings.value.size,
            "elastic": settings.value.elastic,
            "model_type": settings.value.model_type
        }
    }
)
)

async function askQuestion() {
    const {
        data: answers,
        pending,
        error,
        refresh,
    } = await useAsyncData("answers", () =>
        // $fetch(`/api/qa`,
        $fetch(`${config.apiUrl}/qa`,
            {
                method: 'POST',
                body: {
                    "query": question.value,
                    "size": settings.value.size,
                    "elastic": settings.value.elastic,
                    "model_type": settings.value.model_type
                }
            }
        )
    )
}
</script>