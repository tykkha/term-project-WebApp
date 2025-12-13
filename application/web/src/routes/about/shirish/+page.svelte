<script>
    import Person from '../../../lib/components/Person.svelte';
</script>

<div class="min-w-screen min-h-screen bg-neutral-100">
    <div class="pt-32">
        <div
                class="mx-auto mb-8 flex w-full max-w-3xl justify-center rounded-2xl bg-white p-6 text-center shadow-lg"
        >
            <Person
                    name="Shirish Maharjan"
                    github="https://github.com/shirishsm5"
                    src="https://avatars.githubusercontent.com/shirishsm5"
                    description={[
					"Hello, my name is Shirish Maharjan. I am a computer science student with a strong interest in design and computer architecture. I enjoy understanding how systems are built from the ground up and exploring the intersection between creativity and technology.",
					"In my free time, I love traveling, exploring new places, and learning about different cultures and histories. I also enjoy diving into historical topics that help broaden my perspective on the world."
				]}
            />
        </div>
    </div>
</div>
