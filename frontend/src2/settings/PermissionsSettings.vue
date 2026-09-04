<script setup lang="tsx">
import { watchDebounced } from '@vueuse/core'
import { Avatar, ListView } from 'frappe-ui'
import { Plus } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import Checkbox from '../components/Checkbox.vue'
import { copy } from '../helpers'
import session from '../session'
import CreateTeamDialog from '../teams/CreateTeamDialog.vue'
import ManageTeamDialog from '../teams/ManageTeamDialog.vue'
import useTeamStore, { Team } from '../teams/teams'
import SettingItem from './SettingItem.vue'
import useSettings from './settings'
//// Neoffice — added import. The whole file's user-facing strings are wrapped in
//// __() (upstream hardcodes English); the French catalogue lives in
//// insights/locale/fr.po. Keep this import when merging upstream's version.
import { __ } from '../translation'

const teamStore = useTeamStore()
teamStore.getTeams()

const settings = useSettings()
settings.load()

watchDebounced(
	() => settings.doc,
	() => {
		if (settings.isdirty) {
			settings.save()
		}
	},
	{ debounce: 500, deep: true }
)

const searchQuery = ref('')
const filteredTeams = computed(() => {
	if (!searchQuery.value) {
		return teamStore.teams
	}
	return teamStore.teams.filter((team) =>
		team.team_name.toLowerCase().includes(searchQuery.value.toLowerCase())
	)
})

const listOptions = ref({
	columns: [
		{
			//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
			label: __('Team Name'),
			key: 'team_name',
			prefix(props: any) {
				const team = props.row as Team
				return <Avatar size="md" label={team.team_name} />
			},
		},
	],
	rows: filteredTeams,
	rowKey: 'team_name',
	options: {
		selectable: false,
		showTooltip: false,
		onRowClick: (team: Team) => {
			editTeam.value = copy(team)
			showEditTeamDialog.value = true
		},
		emptyState: {
			//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
			title: __('No teams.'),
			description: __('No teams to display.'),
			button: session.user.is_admin
				? {
						//// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French
						label: __('Create Team'),
						variant: 'solid',
						onClick: () => (showCreateTeamDialog.value = true),
				  }
				: undefined,
		},
	},
})

const showCreateTeamDialog = ref(false)
const showEditTeamDialog = ref(false)
const editTeam = ref<Team | null>(null)
</script>

<template>
	<div class="flex w-full flex-col gap-6 overflow-y-scroll p-8 px-10">
		<!-- //// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French -->
		<h1 class="text-xl font-semibold">{{ __("Permissions") }}</h1>

		<!-- //// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French -->
		<SettingItem
			:label="__('Enable')"
			:description="__('Enable permissions to restrict access to data sources & tables based on teams and users.')"
		>
			<Toggle v-model="settings.doc.enable_permissions" />
		</SettingItem>

		<!-- //// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French -->
		<SettingItem
			:label="__('Apply User Permissions')"
			:description="__('Apply restrictions based on roles and user permissions defined on this site. Only applicable for site data source.')"
		>
			<Toggle v-model="settings.doc.apply_user_permissions" />
		</SettingItem>

		<div class="flex w-full flex-1 flex-col gap-3 overflow-auto">
			<!-- //// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French -->
			<SettingItem
				:label="__('Teams')"
				:description="__('Create teams to group users and manage permissions.')"
			>
				<!-- //// Neoffice — __() wrapping: upstream hardcodes English, our fleet is French — the :label on this
				     //// Button is 3 lines inside its own multi-line opening tag, where no comment
				     //// can live; this marker on the element is the closest reachable spot (see
				     //// NEOFFICE_FORK_MARKERS.md, "Hunks a comment cannot reach"). -->
				<Button
					v-if="session.user.is_admin"
					class="self-end"
					:label="__('New Team')"
					variant="outline"
					@click="showCreateTeamDialog = true"
				>
					<template #prefix>
						<Plus class="h-4 w-4 text-gray-700" stroke-width="1.5" />
					</template>
				</Button>
			</SettingItem>
			<ListView class="h-full" v-bind="listOptions"> </ListView>
		</div>
	</div>

	<CreateTeamDialog v-model="showCreateTeamDialog" />

	<ManageTeamDialog
		v-if="editTeam"
		:key="editTeam.name"
		v-model="showEditTeamDialog"
		:team="editTeam"
	/>
</template>
