<script>
	import { Menu } from '@ark-ui/svelte';
</script>

<nav>
	<div class="fixed top-0 flex w-full flex-row gap-8 bg-white p-8 text-black">
		<img src="/sfsu_logo.png" alt="San Francisco State University Logo" class="max-h-8" />
		<h2 class="text-3xl font-bold">Gator Guides</h2>
		<Menu.Root>
			<Menu.Trigger>Open Menu</Menu.Trigger>
			<Menu.Positioner>
				<Menu.Content>
					<Menu.ItemGroup>
						<Menu.ItemGroupLabel>My Account</Menu.ItemGroupLabel>
						<Menu.Separator />
						<Menu.Item value="profile">
							<!-- <UserIcon /> -->
							Profile
							<span>⇧⌘P</span>
						</Menu.Item>
						<Menu.Item value="billing">
							<!-- <CreditCardIcon />  -->
							Billing
						</Menu.Item>
						<Menu.Item value="settings">
							<!-- <SettingsIcon /> -->
							Settings
							<span>⌘,</span>
						</Menu.Item>
						<Menu.Root positioning={{ placement: 'right-start', gutter: -2 }}>
							<Menu.TriggerItem>
								<!-- <UserPlusIcon /> -->
								Invite member
								<!-- <ChevronRightIcon /> -->
							</Menu.TriggerItem>
							<Menu.Positioner>
								<Menu.Content>
									<Menu.Item value="email">
										<!-- <MailIcon />  -->
										Email
									</Menu.Item>
									<Menu.Item value="message">
										<!-- <MessageSquareIcon />  -->
										Message
									</Menu.Item>
									<Menu.Separator />
									<Menu.Item value="other">
										<!-- <PlusCircleIcon /> -->
										More Options...
									</Menu.Item>
								</Menu.Content>
							</Menu.Positioner>
						</Menu.Root>
						<Menu.Separator />
						<Menu.Item value="logout">
							<!-- <LogOutIcon /> -->
							Logout
						</Menu.Item>
					</Menu.ItemGroup>
				</Menu.Content>
			</Menu.Positioner>
		</Menu.Root>
	</div>
</nav>
