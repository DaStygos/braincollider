"""
Test script to verify LaTeX support in BrainCollider
Run with: python manage.py shell < test_latex.py
"""

from problems.models import Problem

# Create a test problem with LaTeX formulas
test_problem = Problem.objects.create(
    title="Test: Quadratic Formula",
    statement="""
Let's solve a quadratic equation using the quadratic formula:

$$ax^2 + bx + c = 0$$

The solutions are given by:

$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

For example, if $a=1$, $b=-5$, and $c=6$, then:
$$x = \\frac{5 \\pm \\sqrt{25 - 24}}{2} = \\frac{5 \\pm 1}{2}$$

So $x_1 = 3$ and $x_2 = 2$.
    """.strip(),
    category='autre',
    solution="The solutions are x₁ = 3 and x₂ = 2, as shown by the quadratic formula: $x = \\frac{5 \\pm 1}{2}$",
    difficulty=2,
)

print(f"✓ Created test problem: {test_problem.title}")
print(f"  Problem ID: {test_problem.id}")
print(f"  URL: /problems/{test_problem.id}/")
print("\nVisit http://localhost:8000/problems/{0}/ to see LaTeX rendering".format(test_problem.id))
print("\nThe problem statement contains:")
print("  - Inline math: $a$, $b$, $c$, $x$")
print("  - Display math: quadratic equation and quadratic formula")
