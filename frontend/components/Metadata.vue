<template>
    <div class="flex flex-row bg-slate-300 rounded-xl border border-gray-300 p-2 max-w-fit px-3 space-x-2 items-center align-middle hover:bg-slate-400/40 transition duration-300">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"
            class="w-5 h-5 text-gray-600">
            <path stroke-linecap="round" stroke-linejoin="round"
                d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13" />
        </svg>
        <div class="flex flex-col grow space-y-0.5 align-middle">
            <!-- <p class="font-medium">{{ metadata.section }}</p> -->
            <!-- <p class="text-sm">{{ metadata.source }}</p> -->
            <pre class="text-xs">{{ metadata.filename }}</pre>
        </div>
    </div>
</template>

<script setup>
defineProps({
    metadata: {
        section: String,
        source: String,
        filename: String,
    }
})
</script>