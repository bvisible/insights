<!-- //// Neoffice — added file (no upstream equivalent) (maintenance#2651). A signed-in account that holds no
     //// Insights role (a portal customer, a desk user without the role) reached the dashboards' blank shell:
     //// every call answered 403 and the page said nothing and offered no way out. The router now sends it
     //// here: what is going on, and the way back to where the account belongs (its account page for a
     //// portal account, never the desk it cannot use; the desk for a desk user). -->
<template>
	<div class="flex h-full w-full items-center justify-center px-4">
		<div class="flex max-w-md flex-col items-center gap-3 text-center">
			<h1 class="text-2xl font-semibold text-gray-900">
				{{ __('You do not have access to the dashboards.') }}
			</h1>
			<p class="text-base text-gray-600">
				{{ __('Ask your administrator if your work needs them.') }}
			</p>
			<a :href="exit.href" class="mt-2 text-base text-gray-900 underline">{{ exit.label }}</a>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import session from '../session'

// get_user_info is refused to such an account, so has_desk_access is often unknown here: the `system_user` cookie
// frappe sets at sign-in (« yes » for a desk user) says it too.
const exit = computed(() =>
	session.user.has_desk_access || (session.user as Record<string, unknown>).system_user === 'yes'
		? { href: '/app', label: __('Back to the desk') }
		: { href: '/me', label: __('Go to my account') },
)
</script>
