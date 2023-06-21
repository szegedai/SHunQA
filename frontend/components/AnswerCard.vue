<template>
    <div class="rounded-md bg-slate-200 mt-4 p-6 border border-gray-300 hover:bg-slate-300/60 transition duration-300">
        <div class="flex flex-row justify-between">
            <div class="font-medium text-xl text-gray-900">„{{ answer.answer }}”</div>
            <div class="flex flex-row space-x-2">
                <div class="hover:rotate-180 transition duration-300"
                    :title="'Model score: ' + answer.model_score + '\nElastic score: ' + answer.elastic_score">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" class="w-6 h-6 text-lime-600">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M12 12.75c1.148 0 2.278.08 3.383.237 1.037.146 1.866.966 1.866 2.013 0 3.728-2.35 6.75-5.25 6.75S6.75 18.728 6.75 15c0-1.046.83-1.867 1.866-2.013A24.204 24.204 0 0112 12.75zm0 0c2.883 0 5.647.508 8.207 1.44a23.91 23.91 0 01-1.152 6.06M12 12.75c-2.883 0-5.647.508-8.208 1.44.125 2.104.52 4.136 1.153 6.06M12 12.75a2.25 2.25 0 002.248-2.354M12 12.75a2.25 2.25 0 01-2.248-2.354M12 8.25c.995 0 1.971-.08 2.922-.236.403-.066.74-.358.795-.762a3.778 3.778 0 00-.399-2.25M12 8.25c-.995 0-1.97-.08-2.922-.236-.402-.066-.74-.358-.795-.762a3.734 3.734 0 01.4-2.253M12 8.25a2.25 2.25 0 00-2.248 2.146M12 8.25a2.25 2.25 0 012.248 2.146M8.683 5a6.032 6.032 0 01-1.155-1.002c.07-.63.27-1.222.574-1.747m.581 2.749A3.75 3.75 0 0115.318 5m0 0c.427-.283.815-.62 1.155-.999a4.471 4.471 0 00-.575-1.752M4.921 6a24.048 24.048 0 00-.392 3.314c1.668.546 3.416.914 5.223 1.082M19.08 6c.205 1.08.337 2.187.392 3.314a23.882 23.882 0 01-5.223 1.082" />
                    </svg>
                </div>
                <div class="cursor-pointer " title="Feedback" @click="feedback = !feedback">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" class="w-6 h-6 text-orange-600 hover:text-orange-800 transition duration-300">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                    </svg>
                </div>
            </div>
        </div>

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
        <!-- <div v-if="open" class="">
            <p>{{ answer.official_context.slice(0, answer.start) }} <span class="bg-slate-950 text-white rounded">{{
                answer.official_context.slice(answer.start, answer.end) }}</span> {{
        answer.official_context.slice(answer.end, -1) }}</p>
        </div> -->

        <div v-if="open" class="text-slate-900 mb-3">
            <p class="text-justify">
                {{ answer.official_context.slice(0, answer.start) }}
                <span class="before:block before:absolute before:-inset-0.5 before:bg-slate-400 relative inline-block">
                    <span class="relative text-white font-medium">
                        {{ answer.official_context.slice(answer.start, answer.end) }}
                    </span>
                </span>
                {{ answer.official_context.slice(answer.end, -1) }}
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
    </div>
    <Feedback v-if="feedback" :answer="answer" :question="question" :system="system" :close-feedback="toggleOpen" />
</template>

<script setup>
defineProps({
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
    }
})

const open = ref(false)
const feedback = ref(false)

const toggleOpen = () => {
    feedback.value = !feedback.value
}
</script>