<template>
    <div>
        <div v-if="open" class="rounded-md bg-slate-200 my-4 p-4 border border-gray-300 flex flex-col space-y-2">
            <input type="number" min="1" max="3" v-model="settings.size" class="w-16 rounded-md border border-gray-300 p-1" />
            <select v-model="settings.elastic" class="rounded-md border border-gray-300 p-1 bg-white">
                <option v-for="table in elasticTables" :value="table">{{ table }}</option>
            </select>
            <select v-model="settings.model_type" class="rounded-md border border-gray-300 p-1 bg-white">
                <option value="ZTamas/xlm-roberta-large-squad2_impossible_long_answer">
                    ZTamas/xlm-roberta-large-squad2_impossible_long_answer</option>
            </select>
        </div>

        <p v-html="$t('app.description')" class="mb-2"></p>

        <pre class="mb-2 italic">{{ $t('app.exampleQuestion') }}</pre>
        <SearchBar v-model:query="question" :pending="pending" :ask-question="askQuestion" :error="error" class="mb-4"/>
        <AskQuestion v-if="Object.keys(answers.system) == 0" />
        <p v-if="!pending && answers" v-for="answer in answers.answers">
            <AnswerCard :answer="answer" :question="question" :system="answers.system" />
        </p>
    </div>
</template>

<script setup>
defineProps({
    open: Boolean
})

const config = useRuntimeConfig().public
const elasticTables = config.elasticTables.split(",")
const question = ref("")
const settings = ref({
    size: 3,
    elastic: elasticTables[0],
    model_type: "ZTamas/xlm-roberta-large-squad2_impossible_long_answer"
})

const {
    data: answers,
    pending,
    error,
    refresh
} = useAsyncData("answers", () => $fetch(`${config.apiUrl}/qa`,
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