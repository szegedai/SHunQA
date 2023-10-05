<template>
    <div tabindex="-1" aria-hidden="true"
        class="fixed top-0 left-0 right-0 z-50 w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-full max-h-full bg-slate-500/50">
        <div class="relative w-full max-w-md max-h-full h-full mx-auto flex items-center justify-center">

            <div class="relative bg-white rounded-lg shadow grow">
                <button type="button" @click="closeFeedback"
                    class="absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center">
                    <svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd"
                            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                            clip-rule="evenodd"></path>
                    </svg>
                    <span class="sr-only">{{ $t('app.feedback.modal.close') }}</span>
                </button>
                <div class="px-6 py-6 lg:px-8">
                    <h3 class="text-xl font-medium text-gray-900">{{ $t('app.feedback.modal.title') }}</h3>
                    <h4 class="mb-4 text-lg font-light text-gray-800">{{ $t('app.feedback.modal.subtitle') }}</h4>
                    <div class="space-y-4">
                        <div>
                            <label for="what-should-be" class="block mb-2 text-sm font-medium text-gray-900">{{ $t('app.feedback.modal.whatShouldBe') }}</label>
                            <textarea id="what-should-be" v-model="whatShouldBe"
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" />
                        </div>
                        <div>
                            <label for="whats-wrong" class="block mb-2 text-sm font-medium text-gray-900">{{ $t('app.feedback.modal.whatsWrong') }}</label>
                            <textarea id="whats-wrong" v-model="whatsWrong"
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" />
                        </div>
                        <div>
                            <label for="was-this-in-the-context" class="block mb-2 text-sm font-medium text-gray-900">{{ $t('app.feedback.modal.wasThisInTheContext') }}</label>
                            <select id="was-this-in-the-context" v-model="wasThisInTheContext"
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5">
                                <option value="yes">{{ $t('app.feedback.modal.yes') }}</option>
                                <option value="no">{{ $t('app.feedback.modal.no') }}</option>
                                <option value="not-sure">{{ $t('app.feedback.modal.notSure') }}</option>
                            </select>
                        </div>
                        <div>
                            <label for="anything-else" class="block mb-2 text-sm font-medium text-gray-900">{{ $t('app.feedback.modal.anythingElse') }}</label>
                            <textarea id="anything-else" v-model="anythingElse"
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" />
                        </div>
                        <button @click="sendFeedback"
                            class="w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center">
                            {{ $t('app.feedback.modal.send') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    answer: {
        answer: String,
        text_start: Number,
        text_end: Number,
        id: Number,
        context: String,
        elastic_score: [Number],
        model_score: Number,
        metadata: [{
            title: String,
            section: String,
            file_name: String,
        }]
    },
    question: String,
    closeFeedback: Function
})

const whatShouldBe = ref('')
const whatsWrong = ref('')
const anythingElse = ref('')
const wasThisInTheContext = ref('')
const config = useRuntimeConfig().public
const { t } = useI18n()

const sendFeedback = async () => {
    await useAsyncData('feedbackDislike', () => {
        $fetch(`${config.apiUrl}/feedback/dislike`,
            {
                method: 'POST',
                body: {
                    "id": props.answer.id,
                    "what_should_be": whatShouldBe.value,
                    "whats_wrong": whatsWrong.value,
                    "anything_else": anythingElse.value,
                    "was_this_in_the_context": wasThisInTheContext.value,
                }
            }).then((res) => {
                props.closeFeedback()
                useNuxtApp().$toast.success(t('app.feedback.toast.success'))
            }).catch((err) => {
                props.closeFeedback()
                useNuxtApp().$toast.error(t('app.feedback.toast.error'))
            })
    })
}
</script>