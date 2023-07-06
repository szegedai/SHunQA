<template>
    <div class="rounded-md bg-slate-100 p-6 border border-gray-300 hover:bg-slate-200/60 transition duration-300" v-if="answer.relevant_context">
        <div>
            <p class="text-xl font-medium">{{ answer.metadata[0].source }}</p>
            <p class="text-">{{ answer.metadata[0].section }}</p>
        </div>

        <blockquote class="p-4 my-4 border-l-4 border-lime-600 bg-gray-200/80" v-if="answer.answer">
            <p class="italic font-medium leading-relaxed text-gray-900">„{{ answer.answer }}”</p>
        </blockquote>

        <div class="py-3 flex flex-row space-x-3 hover:brightness-125 transition duration-300 cursor-pointer"
            @click="open = !open">
            <hr class="grow h-0.5 my-2 bg-gray-400 border-0" />
            <div class="text-gray-500">
                <template v-if="!open">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M3 4.5h14.25M3 9h9.75M3 13.5h9.75m4.5-4.5v12m0 0l-3.75-3.75M17.25 21L21 17.25" />
                    </svg>
                </template>
                <template v-else>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M3 4.5h14.25M3 9h9.75M3 13.5h5.25m5.25-.75L17.25 9m0 0L21 12.75M17.25 9v12" />
                    </svg>
                </template>
            </div>
            <hr class="grow h-0.5 my-2 bg-gray-400 border-0" />
        </div>

        <div v-if="open" class="text-slate-900 mb-3 flex flex-col space-y-2">
            <h2 class="text-gray-500">Context</h2>
            <p class="text-justify">
                {{ answer.relevant_context.slice(0, answer.start) }}
                <span class="before:block before:absolute before:-inset-0.5 before:bg-slate-400 relative inline-block" v-if="answer.end != 0">
                    <span class="relative text-white font-medium">
                        {{ answer.relevant_context.slice(answer.start, answer.end) }}
                    </span>
                </span>
                {{ answer.relevant_context.slice(answer.end, -1) }}
            </p>

            <!-- 
            <div class="text-gray-500 text-sm">
                <p class="text-gray-500">Model score: {{ answer.model_score }}</p>
                <p class="text-gray-500">Elastic score: {{ answer.elastic_score }}</p>
            </div> -->
        </div>

        <div class="flex flex-col space-y-2" v-if="answer.metadata">
            <h2 class="text-gray-500">Attachments</h2>
            <div class="flex flex-row space-x-2">
                <Metadata v-for="metadata in answer.metadata" :metadata="metadata" />
            </div>
        </div>
        <div class="flex flex-row space-x-2 justify-end">
            <div class="hover:rotate-180 transition duration-300" v-if="config.debug"
                :title="'Model score: ' + answer.model_score + '\nElastic score: ' + answer.elastic_score">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                    stroke="currentColor" class="w-6 h-6 text-lime-600">
                    <path stroke-linecap="round" stroke-linejoin="round"
                        d="M12 12.75c1.148 0 2.278.08 3.383.237 1.037.146 1.866.966 1.866 2.013 0 3.728-2.35 6.75-5.25 6.75S6.75 18.728 6.75 15c0-1.046.83-1.867 1.866-2.013A24.204 24.204 0 0112 12.75zm0 0c2.883 0 5.647.508 8.207 1.44a23.91 23.91 0 01-1.152 6.06M12 12.75c-2.883 0-5.647.508-8.208 1.44.125 2.104.52 4.136 1.153 6.06M12 12.75a2.25 2.25 0 002.248-2.354M12 12.75a2.25 2.25 0 01-2.248-2.354M12 8.25c.995 0 1.971-.08 2.922-.236.403-.066.74-.358.795-.762a3.778 3.778 0 00-.399-2.25M12 8.25c-.995 0-1.97-.08-2.922-.236-.402-.066-.74-.358-.795-.762a3.734 3.734 0 01.4-2.253M12 8.25a2.25 2.25 0 00-2.248 2.146M12 8.25a2.25 2.25 0 012.248 2.146M8.683 5a6.032 6.032 0 01-1.155-1.002c.07-.63.27-1.222.574-1.747m.581 2.749A3.75 3.75 0 0115.318 5m0 0c.427-.283.815-.62 1.155-.999a4.471 4.471 0 00-.575-1.752M4.921 6a24.048 24.048 0 00-.392 3.314c1.668.546 3.416.914 5.223 1.082M19.08 6c.205 1.08.337 2.187.392 3.314a23.882 23.882 0 01-5.223 1.082" />
                </svg>
            </div>
            <div class="cursor-pointer text-blue-600 hover:text-blue-800 transition duration-300" title="I like this answer"
                @click="sendFeedback">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                    stroke="currentColor" class="w-6 h-6">
                    <path stroke-linecap="round" stroke-linejoin="round"
                        d="M6.633 10.5c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 01.75-.75A2.25 2.25 0 0116.5 4.5c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 01-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 00-1.423-.23H5.904M14.25 9h2.25M5.904 18.75c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 01-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 10.203 4.167 9.75 5 9.75h1.053c.472 0 .745.556.5.96a8.958 8.958 0 00-1.302 4.665c0 1.194.232 2.333.654 3.375z" />
                </svg>
            </div>
            <div class="cursor-pointer text-orange-600 hover:text-orange-800 transition duration-300"
                title="I don't like this answer" @click="feedback = !feedback">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                    stroke="currentColor" class="w-6 h-6">
                    <path stroke-linecap="round" stroke-linejoin="round"
                        d="M7.5 15h2.25m8.024-9.75c.011.05.028.1.052.148.591 1.2.924 2.55.924 3.977a8.96 8.96 0 01-.999 4.125m.023-8.25c-.076-.365.183-.75.575-.75h.908c.889 0 1.713.518 1.972 1.368.339 1.11.521 2.287.521 3.507 0 1.553-.295 3.036-.831 4.398C20.613 14.547 19.833 15 19 15h-1.053c-.472 0-.745-.556-.5-.96a8.95 8.95 0 00.303-.54m.023-8.25H16.48a4.5 4.5 0 01-1.423-.23l-3.114-1.04a4.5 4.5 0 00-1.423-.23H6.504c-.618 0-1.217.247-1.605.729A11.95 11.95 0 002.25 12c0 .434.023.863.068 1.285C2.427 14.306 3.346 15 4.372 15h3.126c.618 0 .991.724.725 1.282A7.471 7.471 0 007.5 19.5a2.25 2.25 0 002.25 2.25.75.75 0 00.75-.75v-.633c0-.573.11-1.14.322-1.672.304-.76.93-1.33 1.653-1.715a9.04 9.04 0 002.86-2.4c.498-.634 1.226-1.08 2.032-1.08h.384" />
                </svg>
            </div>
        </div>
    </div>
    <NoAnswer v-if="!answer.relevant_context" />
    <Feedback v-if="feedback" :answer="answer" :question="question" :system="system" :close-feedback="toggleOpen" />
</template>

<script setup>
const config = useRuntimeConfig().public

const props = defineProps({
    answer: {
        answer: String,
        start: Number,
        end: Number,
        id: Number,
        lemmatized_context: String,
        official_context: String,
        model_score: Number,
        elastic_score: Number,
        metadata: [{
            section: String,
            source: String,
            filename: String,
        }]
    },
    question: String,
    system: {
        query: String,
        size: Number,
        elastic: String,
        model_type: String,
        time: Number,
        id: String,
    }
})

const open = ref(false)
const feedback = ref(false)

const toggleOpen = () => {
    feedback.value = !feedback.value
}

const sendFeedback = async () => {
    await useAsyncData('feedbackLike', () => {
        $fetch(`${config.apiUrl}/feedback/like`, 
        {
            method: 'POST',
            body: {
                "id": props.system.id,
            }
        }
        ).then(() => {
            useNuxtApp().$toast.success('Thank you for your feedback!')
        }).catch(() => {
            useNuxtApp().$toast.error('Something went wrong with sending your feedback. Please try again later.')
        })
    })
}
</script>