(function () {
  const canvas = document.createElement('canvas');
  canvas.id = 'auth-bg';
  document.body.prepend(canvas);
  const context = canvas.getContext('2d');

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  resize();
  window.addEventListener('resize', resize);

  const primary = '#4b5bdc';

  function hexAlpha(hex, alpha) {
    const red = parseInt(hex.slice(1, 3), 16);
    const green = parseInt(hex.slice(3, 5), 16);
    const blue = parseInt(hex.slice(5, 7), 16);
    return `rgba(${red},${green},${blue},${alpha})`;
  }

  const triangles = Array.from({length: 18}, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    size: 30 + Math.random() * 60,
    angle: Math.random() * Math.PI * 2,
    speed: (Math.random() - 0.5) * 0.3,
    rotSpeed: (Math.random() - 0.5) * 0.008,
    alpha: 0.05 + Math.random() * 0.12,
    filled: Math.random() > 0.5,
  }));

  function draw() {
    const width = canvas.width;
    const height = canvas.height;
    context.clearRect(0, 0, width, height);

    for (const triangle of triangles) {
      triangle.angle += triangle.rotSpeed;
      triangle.y += triangle.speed;
      if (triangle.y > height + triangle.size) triangle.y = -triangle.size;
      if (triangle.y < -triangle.size) triangle.y = height + triangle.size;

      context.save();
      context.translate(triangle.x, triangle.y);
      context.rotate(triangle.angle);
      context.beginPath();
      context.moveTo(0, -triangle.size / 2);
      context.lineTo(triangle.size / 2, triangle.size / 2);
      context.lineTo(-triangle.size / 2, triangle.size / 2);
      context.closePath();

      if (triangle.filled) {
        context.fillStyle = hexAlpha(primary, triangle.alpha);
        context.fill();
      } else {
        context.strokeStyle = hexAlpha(primary, triangle.alpha + 0.05);
        context.lineWidth = 1.5;
        context.stroke();
      }

      context.restore();
    }

    requestAnimationFrame(draw);
  }

  draw();
})();
