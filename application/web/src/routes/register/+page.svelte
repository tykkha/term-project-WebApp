<script lang="ts">
    import { goto } from '$app/navigation';

    // Form state
    let formData = $state({
        // Personal Information
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        studentId: '',

        // Account Security
        password: '',
        confirmPassword: '',

        // Tutor Information
        major: '',
        gpa: '',
        graduationYear: '',
        bio: '',

        // Subjects and Availability
        subjects: [] as string[],
        availability: {
            monday: false,
            tuesday: false,
            wednesday: false,
            thursday: false,
            friday: false,
            saturday: false,
            sunday: false
        },

        // Agreement
        agreeToTerms: false
    });

    let currentSubject = $state('');
    let errorMessage = $state('');
    let successMessage = $state('');

    //temp
    const availableSubjects = [
        'CSC 101',
        'CSC 210',
        'CSC 220',
        'CSC 413',
        'CSC 415',
        'CSC 648',
        'MATH 226',
        'MATH 227',
        'PHYS 220',
        'PHYS 230',
        'CHEM 115',
        'BIOL 230'
    ];

    function addSubject() {
        if (currentSubject && !formData.subjects.includes(currentSubject)) {
            formData.subjects = [...formData.subjects, currentSubject];
            currentSubject = '';
        }
    }

    function removeSubject(subject: string) {
        formData.subjects = formData.subjects.filter((s) => s !== subject);
    }

    function validateForm(): boolean {
        errorMessage = '';

        if (!formData.firstName || !formData.lastName) {
            errorMessage = 'Please enter your full name';
            return false;
        }

        if (!formData.email.includes('@')) {
            errorMessage = 'Please enter a valid email address';
            return false;
        }

        if (!formData.studentId) {
            errorMessage = 'Please enter your student ID';
            return false;
        }

        if (formData.password.length < 8) {
            errorMessage = 'Password must be at least 8 characters long';
            return false;
        }

        if (formData.password !== formData.confirmPassword) {
            errorMessage = 'Passwords do not match';
            return false;
        }

        if (!formData.major || !formData.gpa) {
            errorMessage = 'Please complete the tutor information section';
            return false;
        }

        const gpaNum = parseFloat(formData.gpa);
        if (isNaN(gpaNum) || gpaNum < 0 || gpaNum > 4.0) {
            errorMessage = 'Please enter a valid GPA between 0.0 and 4.0';
            return false;
        }

        if (formData.subjects.length === 0) {
            errorMessage = 'Please add at least one subject you can tutor';
            return false;
        }

        if (!formData.agreeToTerms) {
            errorMessage = 'Please agree to the terms and conditions';
            return false;
        }

        return true;
    }

    function handleSubmit() {
        if (!validateForm()) {
            return;
        }

        // TODO: Send data to backend API
        console.log('Form submitted:', formData);

        successMessage = 'Registration successful! Redirecting to login...';

        setTimeout(() => {
            goto('/');
        }, 2000);
    }
</script>

<div class="min-h-screen bg-neutral-100 py-8">
    <div class="mx-auto max-w-4xl px-4">
        <!-- Header -->
        <div class="mb-8 text-center">
            <h1 class="mb-2 text-4xl font-bold text-[#231161]">Become a Gator Guide Tutor</h1>
            <p class="text-gray-600">Join our community of peer tutors helping fellow students succeed</p>
        </div>

        <!-- Form Container -->
        <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="rounded-2xl bg-white p-8 shadow-lg">
            <!-- Personal Information Section -->
            <section class="mb-8">
                <h2 class="mb-4 text-2xl font-bold text-gray-800">Personal Information</h2>
                <div class="grid gap-4 md:grid-cols-2">
                    <div>
                        <label for="firstName" class="mb-2 block text-sm font-medium text-gray-700">
                            First Name <span class="text-red-500">*</span>
                        </label>
                        <input id="firstName" type="text" bind:value={formData.firstName} required class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                    <div>
                        <label for="lastName" class="mb-2 block text-sm font-medium text-gray-700">
                            Last Name <span class="text-red-500">*</span>
                        </label>
                        <input id="lastName" type="text" bind:value={formData.lastName} required class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                    <div>
                        <label for="email" class="mb-2 block text-sm font-medium text-gray-700">
                            SFSU Email <span class="text-red-500">*</span>
                        </label>
                        <input id="email" type="email" bind:value={formData.email} placeholder="you@sfsu.edu" required class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                    <div>
                        <label for="phone" class="mb-2 block text-sm font-medium text-gray-700">Phone Number</label>
                        <input id="phone" type="tel" bind:value={formData.phone} placeholder="(123) 456-7890" class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                    <div class="md:col-span-2">
                        <label for="studentId" class="mb-2 block text-sm font-medium text-gray-700">
                            Student ID <span class="text-red-500">*</span>
                        </label>
                        <input id="studentId" type="text" bind:value={formData.studentId} placeholder="920123456" required class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                </div>
            </section>

            <!-- Account Security Section -->
            <section class="mb-8">
                <h2 class="mb-4 text-2xl font-bold text-gray-800">Account Security</h2>
                <div class="grid gap-4 md:grid-cols-2">
                    <div>
                        <label for="password" class="mb-2 block text-sm font-medium text-gray-700">
                            Password <span class="text-red-500">*</span>
                        </label>
                        <input id="password" type="password" bind:value={formData.password} placeholder="At least 8 characters" required class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                    <div>
                        <label for="confirmPassword" class="mb-2 block text-sm font-medium text-gray-700">
                            Confirm Password <span class="text-red-500">*</span>
                        </label>
                        <input id="confirmPassword" type="password" bind:value={formData.confirmPassword} placeholder="Re-enter password" required class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                </div>
            </section>

            <!-- Tutor Information Section -->
            <section class="mb-8">
                <h2 class="mb-4 text-2xl font-bold text-gray-800">Tutor Information</h2>
                <div class="grid gap-4 md:grid-cols-2">
                    <div>
                        <label for="major" class="mb-2 block text-sm font-medium text-gray-700">
                            Major <span class="text-red-500">*</span>
                        </label>
                        <input id="major" type="text" bind:value={formData.major} placeholder="Computer Science" required class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                    <div>
                        <label for="gpa" class="mb-2 block text-sm font-medium text-gray-700">
                            GPA <span class="text-red-500">*</span>
                        </label>
                        <input id="gpa" type="number" step="0.01" min="0" max="4" bind:value={formData.gpa} placeholder="3.50" required class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                    <div class="md:col-span-2">
                        <label for="graduationYear" class="mb-2 block text-sm font-medium text-gray-700">Expected Graduation Year</label>
                        <input id="graduationYear" type="text" bind:value={formData.graduationYear} placeholder="2026" class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50" />
                    </div>
                    <div class="md:col-span-2">
                        <label for="bio" class="mb-2 block text-sm font-medium text-gray-700">Bio / Teaching Philosophy</label>
                        <textarea id="bio" bind:value={formData.bio} rows="4" placeholder="Tell us about your tutoring experience and teaching style..." class="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50"></textarea>
                    </div>
                </div>
            </section>

            <!-- Subjects Section -->
            <section class="mb-8">
                <h2 class="mb-4 text-2xl font-bold text-gray-800">
                    Subjects <span class="text-red-500">*</span>
                </h2>
                <div class="mb-4 flex gap-2">
                    <select bind:value={currentSubject} class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 focus:border-[#231161] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-opacity-50">
                        <option value="">Select a subject</option>
                        {#each availableSubjects as subject}
                            <option value={subject}>{subject}</option>
                        {/each}
                    </select>
                    <button type="button" onclick={addSubject} class="rounded-lg bg-[#231161] px-6 py-2.5 font-medium text-white hover:bg-[#1a0d4a]">
                        Add
                    </button>
                </div>
                {#if formData.subjects.length > 0}
                    <div class="flex flex-wrap gap-2">
                        {#each formData.subjects as subject}
                            <div class="flex items-center gap-2 rounded-full bg-[#231161] px-4 py-2 text-white">
                                <span>{subject}</span>
                                <button type="button" onclick={() => removeSubject(subject)} class="rounded-full hover:bg-white hover:bg-opacity-20" aria-label="Remove {subject}">
                                    ✕
                                </button>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <p class="text-sm text-gray-500">No subjects added yet</p>
                {/if}
            </section>

            <!-- Availability Section -->
            <section class="mb-8">
                <h2 class="mb-4 text-2xl font-bold text-gray-800">Availability</h2>
                <div class="grid gap-3 md:grid-cols-2">
                    {#each Object.keys(formData.availability) as day}
                        <label class="flex items-center gap-3 rounded-lg border border-gray-200 p-3 hover:bg-gray-50">
                            <input type="checkbox" bind:checked={formData.availability[day]} class="h-5 w-5 rounded border-gray-300 text-[#231161] focus:ring-[#231161]" />
                            <span class="font-medium capitalize text-gray-700">{day}</span>
                        </label>
                    {/each}
                </div>
            </section>

            <!-- Terms and Conditions -->
            <section class="mb-6">
                <label class="flex items-start gap-3">
                    <input type="checkbox" bind:checked={formData.agreeToTerms} required class="mt-1 h-5 w-5 rounded border-gray-300 text-[#231161] focus:ring-[#231161]" />
                    <span class="text-sm text-gray-700">
						I agree to the <a href="/terms" class="text-[#231161] hover:underline">Terms and Conditions</a>
						and
						<a href="/privacy" class="text-[#231161] hover:underline">Privacy Policy</a>
						<span class="text-red-500">*</span>
					</span>
                </label>
            </section>

            <!-- Error/Success Messages -->
            {#if errorMessage}
                <div class="mb-4 rounded-lg bg-red-50 p-4 text-red-600">{errorMessage}</div>
            {/if}

            {#if successMessage}
                <div class="mb-4 rounded-lg bg-green-50 p-4 text-green-600">{successMessage}</div>
            {/if}

            <!-- Submit Button -->
            <div class="flex gap-4">
                <a href="/" class="flex-1 rounded-lg border-2 border-gray-300 px-6 py-3 text-center font-semibold text-gray-700 transition-colors hover:bg-gray-50">
                    Cancel
                </a>
                <button type="submit" class="flex-1 rounded-lg bg-[#231161] px-6 py-3 font-semibold text-white transition-colors hover:bg-[#1a0d4a] focus:outline-none focus:ring-2 focus:ring-[#231161] focus:ring-offset-2">
                    Register as Tutor
                </button>
            </div>

            <!-- Login Link -->
            <div class="mt-6 text-center">
                <p class="text-sm text-gray-600">
                    Already have an account?
                    <a href="/login" class="font-medium text-[#231161] hover:underline">Sign in</a>
                </p>
            </div>
        </form>
    </div>
</div>