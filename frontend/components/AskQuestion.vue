<template>
    <Vue3Lottie :animation-data="FAQJson" :height="400" :width="400" />

    <Alert :text="$t('app.alerts.startQuestioning')" color="blue" v-if="!pending" />
    <Alert :text="$t('app.alerts.workingOnIt')" color="gray" v-else />
</template>

<script setup>
import FAQJson from '~/assets/animations/138566-frequently-asked-question-faq.json'
defineProps({
    pending: Boolean,
})

const { t } = useI18n()
</script>