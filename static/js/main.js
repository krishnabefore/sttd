// ============================================================
// StudyPath — frontend interactions
// Part A: onboarding form (index.html)
// Part B: dashboard course ticks (dashboard.html)
// ============================================================

document.addEventListener('DOMContentLoaded', () => {

  /* ---------------- Part A: onboarding form ---------------- */
  const form = document.getElementById('onboardForm');
  if (form) {
    const screens = [...form.querySelectorAll('.screen')];
    let current = 1;

    const answers = { education: null, level: null, goal: null, budget: null };

    function showStep(n) {
      screens.forEach(s => s.classList.toggle('active', Number(s.dataset.step) === n));
      current = n;
    }

    // pill selection (single-select per group)
    form.querySelectorAll('.pill-group').forEach(group => {
      group.addEventListener('click', (e) => {
        const btn = e.target.closest('.pill');
        if (!btn) return;
        group.querySelectorAll('.pill').forEach(p => p.classList.remove('selected'));
        btn.classList.add('selected');
        if (group.id === 'educationGroup') answers.education = btn.dataset.value;
        if (group.id === 'levelGroup') answers.level = btn.dataset.value;
        if (group.id === 'goalGroup') answers.goal = btn.dataset.value;
        if (group.id === 'budgetGroup') {
          answers.budget = btn.dataset.value;
          document.getElementById('submitBtn').disabled = false;
        }
      });
    });

    form.querySelectorAll('[data-next]').forEach(btn => {
      btn.addEventListener('click', () => {
        if (current === 1) {
          if (!document.getElementById('name').value.trim()) {
            document.getElementById('name').focus();
            return;
          }
          if (!answers.education) return;
        }
        if (current === 2 && !document.getElementById('subject').value.trim()) {
          document.getElementById('subject').focus();
          return;
        }
        if (current === 3 && !answers.level) return;
        if (current === 4 && !answers.goal) return;
        if (current < 5) showStep(current + 1);
      });
    });

    form.querySelectorAll('[data-back]').forEach(btn => {
      btn.addEventListener('click', () => {
        if (current > 1) showStep(current - 1);
      });
    });

    // Copy the pill choices into hidden inputs, then the browser POSTs
    // the form to Flask's /build-plan route.
    form.addEventListener('submit', () => {
      form.elements.education.value = answers.education;
      form.elements.level.value = answers.level;
      form.elements.goal.value = answers.goal;
      form.elements.budget.value = answers.budget;
    });
  }

  /* ---------------- Part B: dashboard "watched" ticks ---------------- */
  // Ticks are a personal checklist. Topic progress comes from passing the quiz.
  document.querySelectorAll('.check').forEach(box => {
    box.addEventListener('click', async () => {
      // Ask Flask to flip this item's "done" flag in MySQL
      const res = await fetch(`/api/items/${box.dataset.item}/toggle`, { method: 'POST' });
      if (!res.ok) return;
      const data = await res.json();
      box.classList.toggle('checked', data.done);
    });
  });

});
