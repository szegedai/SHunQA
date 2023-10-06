<template>
    <Vue3Lottie :animation-data="NotSureJson" :height="400" :width="400" v-if="error == 'out_of_domain'" />
    <Vue3Lottie :animation-data="NoAnswerJson" :height="400" :width="400" v-else-if="error == 'reader_failed'" />
    <Vue3Lottie :animation-data="UnknownErrorJson" :height="400" :width="400" v-else />

    <Alert :text="$t('app.alerts.errors.outOfDomain')" color="red" v-if="error == 'out_of_domain'" />
    <Alert :text="$t('app.alerts.errors.noAnswer')" color="red" v-else-if="error == 'reader_failed'" />
    <Alert :text="$t('app.alerts.errors.unknownError')" color="red" v-else />
</template>

<script setup>
defineProps({
    error: String,
})
import NoAnswerJson from '~/assets/animations/98448-no-task.json'
import NotSureJson from '~/assets/animations/animation_lnbn2hfv.json'
import UnknownErrorJson from '~/assets/animations/animation_lnbnam65.json'
</script>