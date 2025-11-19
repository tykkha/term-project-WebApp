<script lang="ts">
	import { Calendar, Clock, BookOpen, User, Search } from '@lucide/svelte';
	import { onMount } from 'svelte';
	//user data to be fetched from backend

	type Appointment = {
		subject: string;
		status: string;
		tutorName: string;
		date: string;
		time: string;
		location: string;
		id: number;
	};
	type Tutor = {
  name:string;
	subject:string;
	rating:number;
	availability:string;
	id:number
	}

	let userData = $state({
		name: '',
		email: '',
		studentId: '',
		role: 'student',
		courses: []
	});
	//appointments will be fetched from backend
	let appointments = $state<Appointment[]>([]);
	//available tutors will be fetched from backend
	let availableTutors = $state<Tutor[]>([]);

	//loading states
	let isLoading = $state(true);
	let error = $state('');

	//filter states
	let searchQuery = $state('');
	let selectedSubject = $state('all');
	let selectedAvailability = $state('all');

	//fetch user data from backend
	async function loadUserData() {
		try {
			//replace with backend
			//const response = await fetch('/api/users/me');
			//const data = await response.json();
			//userData = data;

			console.log('TODO: Fetch user data from /api/users/me');
		} catch (err) {
			error = 'Failed to load user data';
			console.error(err);
		}
	}

	//fetch appointments from backend
	async function loadAppointments() {
		try {
			//Replace with  backend
			// const response = await fetch('/api/appointments');
			// const data = await response.json();
			// appointments = data;

			console.log('TODO: Fetch appointments from /api/appointments');
		} catch (err) {
			error = 'Failed to load appointments';
			console.error(err);
		}
	}

	//fetch available tutors from backend
	async function loadTutors() {
		try {
			//replace with backend endpoint
			//const response = await fetch('/api/tutors/search');
			//const data = await response.json();
			//availableTutors = data;

			console.log('TODO: Fetch tutors from /api/tutors/search');
		} catch (err) {
			error = 'Failed to load tutors';
			console.error(err);
		}
	}
	// Load data when component mounts
	onMount(async () => {
		isLoading = true;
		await Promise.all([loadUserData(), loadAppointments(), loadTutors()]);
		isLoading = false;
	});

	// Reload tutors when filters change
	$effect(() => {
		if (!isLoading) {
			loadTutors();
		}
	});
	function handleBookAppointment(tutorId: number) {
		//Connect to backend
		alert('Backend connection needed: POST /api/appointments/book');
	}

	function handleCancelAppointment(appointmentId: number) {
		const confirmed = confirm('Are you sure you want to cancel this appointment?');
		if (!confirmed) return;

		//Connect to backend
		alert('Backend connection needed: DELETE /api/appointments/' + appointmentId);
	}

	function handleEditProfile() {
		alert('Profile editing will be implemented in next milestone');
	}
</script>

<div class="min-h-screen bg-neutral-100 p-6">
	<div class="mx-auto max-w-7xl">
		{#if isLoading}
			<div class="flex min-h-[60vh] items-center justify-center">
				<div class="text-center">
					<Clock size={64} class="mx-auto mb-4 animate-pulse text-gray-400" />
					<p class="text-xl text-gray-600">Loading your dashboard...</p>
					<p class="mt-2 text-sm text-gray-500">Waiting for backend connection</p>
				</div>
			</div>
		{:else if error}
			<div class="flex min-h-[60vh] items-center justify-center">
				<div class="text-center">
					<div
						class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100"
					>
						<span class="text-2xl text-red-600">!</span>
					</div>
					<p class="text-xl text-red-600">{error}</p>
					<button
						onclick={() => window.location.reload()}
						class="mt-4 rounded-lg bg-[#231161] px-6 py-2 text-white hover:bg-[#1a0d4a]"
					>
						Retry
					</button>
				</div>
			</div>
		{:else}
			<div class="mb-8">
				<h1 class="mb-2 text-4xl font-bold text-[#231161]">
					Welcome back{userData.name ? ', ' + userData.name.split(' ')[0] : ''}!
				</h1>
				<p class="text-gray-600">Here's your tutoring dashboard</p>
			</div>

			<div class="mb-8 grid gap-6 md:grid-cols-3">
				<div class="rounded-2xl bg-white p-6 shadow-lg">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium text-gray-600">Upcoming Sessions</p>
							<p class="mt-2 text-3xl font-bold text-[#231161]">{appointments.length}</p>
						</div>
						<div class="rounded-full bg-[#ffdc70] p-3">
							<Calendar size={24} class="text-[#231161]" />
						</div>
					</div>
				</div>

				<div class="rounded-2xl bg-white p-6 shadow-lg">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium text-gray-600">Active Courses</p>
							<p class="mt-2 text-3xl font-bold text-[#231161]">{userData.courses?.length || 0}</p>
						</div>
						<div class="rounded-full bg-[#ffdc70] p-3">
							<BookOpen size={24} class="text-[#231161]" />
						</div>
					</div>
				</div>

				<div class="rounded-2xl bg-white p-6 shadow-lg">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium text-gray-600">Total Study Hours</p>
							<p class="mt-2 text-3xl font-bold text-[#231161]">0</p>
						</div>
						<div class="rounded-full bg-[#ffdc70] p-3">
							<Clock size={24} class="text-[#231161]" />
						</div>
					</div>
				</div>
			</div>

			<div class="grid gap-8 lg:grid-cols-3">
				<div class="lg:col-span-2">
					<section class="mb-8 rounded-2xl bg-white p-6 shadow-lg">
						<h2 class="mb-6 text-2xl font-bold text-gray-800">Upcoming Appointments</h2>
						{#if appointments.length > 0}
							<div class="space-y-4">
								{#each appointments as appointment}
									<div
										class="flex items-start justify-between rounded-xl border border-gray-200 p-4 transition-all hover:border-[#231161] hover:shadow-md"
									>
										<div class="flex-1">
											<div class="mb-2 flex items-center gap-2">
												<h3 class="text-lg font-semibold text-gray-800">{appointment.subject}</h3>
												<span
													class="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700"
												>
													{appointment.status}
												</span>
											</div>
											<p class="mb-1 text-gray-600">
												<strong>Tutor:</strong>
												{appointment.tutorName}
											</p>
											<p class="mb-1 text-gray-600">
												<Calendar class="mr-1 inline-block" size={16} />
												{appointment.date} at {appointment.time}
											</p>
											<p class="text-gray-600"><span class="mr-1"></span>{appointment.location}</p>
										</div>
										<div class="flex flex-col gap-2">
											<button
												class="rounded-lg bg-[#231161] px-4 py-2 text-sm font-medium text-white hover:bg-[#1a0d4a]"
											>
												Join Session
											</button>
											<button
												onclick={() => handleCancelAppointment(appointment.id)}
												class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
											>
												Cancel
											</button>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="py-12 text-center">
								<Calendar size={48} class="mx-auto mb-4 text-gray-300" />
								<p class="text-gray-500">No upcoming appointments scheduled</p>
								<p class="mt-2 text-sm text-gray-400">Book a session with a tutor to get started</p>
							</div>
						{/if}
					</section>

					<section class="rounded-2xl bg-white p-6 shadow-lg">
						<h2 class="mb-6 text-2xl font-bold text-gray-800">Find Tutors</h2>

						<div class="mb-6 grid gap-4 md:grid-cols-3">
							<div class="relative">
								<Search size={20} class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
								<input
									type="text"
									bind:value={searchQuery}
									placeholder="Search tutors..."
									class="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
								/>
							</div>
							<select
								bind:value={selectedSubject}
								class="rounded-lg border border-gray-300 px-4 py-2 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
							>
								<option value="all">All Subjects</option>
								{#each userData.courses || [] as course}
									<option value={course}>{course}</option>
								{/each}
							</select>
							<select
								bind:value={selectedAvailability}
								class="rounded-lg border border-gray-300 px-4 py-2 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"
							>
								<option value="all">All Availability</option>
								<option value="now">Available Now</option>
								<option value="today">Available Today</option>
								<option value="week">This Week</option>
							</select>
						</div>

						{#if availableTutors.length > 0}
							<div class="space-y-4">
								{#each availableTutors as tutor}
									<div
										class="flex items-center justify-between rounded-xl border border-gray-200 p-4 transition-all hover:border-[#231161] hover:shadow-md"
									>
										<div class="flex items-center gap-4">
											<div
												class="flex h-12 w-12 items-center justify-center rounded-full bg-[#231161]"
											>
												<User size={24} class="text-white" />
											</div>
											<div>
												<h3 class="font-semibold text-gray-800">{tutor.name}</h3>
												<p class="text-sm text-gray-600">{tutor.subject}</p>
												<div class="mt-1 flex items-center gap-2">
													<span class="text-sm text-yellow-500">★ {tutor.rating}</span>
													<span class="text-sm text-gray-500">•</span>
													<span class="text-sm text-green-600">{tutor.availability}</span>
												</div>
											</div>
										</div>
										<button
											onclick={() => handleBookAppointment(tutor.id)}
											class="rounded-lg bg-[#231161] px-6 py-2 font-medium text-white hover:bg-[#1a0d4a]"
										>
											Book Session
										</button>
									</div>
								{/each}
							</div>
						{:else}
							<div class="py-12 text-center">
								<User size={48} class="mx-auto mb-4 text-gray-300" />
								<p class="text-gray-500">No tutors found</p>
								<p class="mt-2 text-sm text-gray-400">Try adjusting your search filters</p>
							</div>
						{/if}
					</section>
				</div>

				<div class="lg:col-span-1">
					<section class="mb-8 rounded-2xl bg-white p-6 shadow-lg">
						<h2 class="mb-4 text-xl font-bold text-gray-800">Your Profile</h2>
						<div class="mb-4 flex items-center justify-center">
							<div
								class="flex h-24 w-24 items-center justify-center rounded-full bg-[#231161] text-3xl font-bold text-white"
							>
								{userData.name
									? userData.name
											.split(' ')
											.map((n) => n[0])
											.join('')
									: '?'}
							</div>
						</div>
						<div class="text-center">
							<h3 class="mb-1 text-lg font-semibold text-gray-800">
								{userData.name || 'Loading...'}
							</h3>
							<p class="mb-2 text-sm text-gray-600">{userData.email || 'Loading...'}</p>
							<p class="mb-4 text-sm text-gray-600">ID: {userData.studentId || 'Loading...'}</p>
							<button
								onclick={handleEditProfile}
								class="w-full rounded-lg border border-[#231161] px-4 py-2 font-medium text-[#231161] hover:bg-[#231161] hover:text-white"
							>
								Edit Profile
							</button>
						</div>
					</section>

					<section class="mb-8 rounded-2xl bg-white p-6 shadow-lg">
						<h2 class="mb-4 text-xl font-bold text-gray-800">Your Courses</h2>
						{#if userData.courses && userData.courses.length > 0}
							<div class="space-y-2">
								{#each userData.courses as course}
									<div
										class="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 font-medium text-gray-700"
									>
										{course}
									</div>
								{/each}
							</div>
						{:else}
							<p class="py-4 text-center text-gray-500">No courses yet</p>
						{/if}
						<button
							class="mt-4 w-full rounded-lg bg-[#ffdc70] px-4 py-2 font-medium text-[#231161] hover:bg-[#f5d05f]"
						>
							+ Add Course
						</button>
					</section>

					<section class="rounded-2xl bg-white p-6 shadow-lg">
						<h2 class="mb-4 text-xl font-bold text-gray-800">Quick Actions</h2>
						<div class="space-y-2">
							<a
								href="/calendar"
								class="block rounded-lg border border-gray-200 px-4 py-3 text-center font-medium text-gray-700 hover:bg-gray-50"
							>
								View Calendar
							</a>
							<a
								href="/search"
								class="block rounded-lg border border-gray-200 px-4 py-3 text-center font-medium text-gray-700 hover:bg-gray-50"
							>
								Browse Tutors
							</a>
							<button
								class="w-full rounded-lg border border-gray-200 px-4 py-3 font-medium text-gray-700 hover:bg-gray-50"
							>
								Message Center
							</button>
						</div>
					</section>
				</div>
			</div>
		{/if}
	</div>
</div>
