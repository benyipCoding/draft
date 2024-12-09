```vue
<template>
  <div id="particles">
    <div class="overlay"></div>
    <div id="intro">
      <h1>3D Animated<br />background</h1>
      <p>Background particle systems</p>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue';

export default {
  name: 'ParticleBackground',
  setup() {
    onMounted(() => {
      // JavaScript for particle animation
      var particle = document.getElementById('particles');
      var count_particles, update, render, canvas, context;
      var max_part = 200;

      // Create canvas element
      var canvas_elm = document.createElement('canvas');
      particle.appendChild(canvas_elm);
      canvas = canvas_elm;
      context = canvas.getContext('2d');

      // Set canvas size to window size
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;

      // Resize canvas when window size changes
      window.onresize = function () {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      };

      // Particle class
      var Particle = function () {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 5 + 1;
        this.speedX = Math.random() * 3 - 1.5;
        this.speedY = Math.random() * 3 - 1.5;
        this.color = 'rgba(' + Math.floor(Math.random() * 255) + ',' + Math.floor(Math.random() * 255) + ',' + Math.floor(Math.random() * 255) + ',0.7)';
      };

      Particle.prototype.update = function () {
        this.x += this.speedX;
        this.y += this.speedY;
        if (this.size > 0.2) this.size -= 0.1;
      };

      Particle.prototype.draw = function () {
        context.fillStyle = this.color;
        context.strokeStyle = this.color;
        context.lineWidth = 2;
        context.beginPath();
        context.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        context.fill();
        context.closePath();
      };

      var particlesArray = [];

      function init() {
        for (var i = 0; i < max_part; i++) {
          particlesArray.push(new Particle());
        }
      }

      function animate() {
        context.clearRect(0, 0, canvas.width, canvas.height);
        for (var i = 0; i < particlesArray.length; i++) {
          particlesArray[i].update();
          particlesArray[i].draw();
          if (particlesArray[i].size <= 0.2) {
            particlesArray.splice(i, 1);
            i--;
          }
        }
        requestAnimationFrame(animate);
      }

      init();
      animate();
    });
  },
};
</script>

<style scoped>
/* CSS Reset */
html,
body,
div,
span,
applet,
object,
iframe,
h1,
h2,
h3,
h4,
h5,
h6,
p,
blockquote,
pre,
a,
abbr,
acronym,
address,
big,
cite,
code,
del,
dfn,
em,
img,
ins,
kbd,
q,
s,
samp,
small,
strike,
strong,
sub,
sup,
tt,
var,
b,
u,
i,
center,
dl,
dt,
dd,
ol,
ul,
li,
fieldset,
form,
label,
legend,
table,
caption,
tbody,
tfoot,
thead,
tr,
th,
td,
article,
aside,
canvas,
details,
embed,
figure,
figcaption,
footer,
header,
hgroup,
menu,
nav,
output,
ruby,
section,
summary,
time,
mark,
audio,
video {
  margin: 0;
  padding: 0;
  border: 0;
  font-size: 100%;
  font: inherit;
  vertical-align: baseline;
}

article,
aside,
details,
figcaption,
figure,
footer,
header,
hgroup,
menu,
nav,
section {
  display: block;
}

body {
  line-height: 1;
}

ol,
ul {
  list-style: none;
}

blockquote,
q {
  quotes: none;
}

blockquote:before,
blockquote:after,
q:before,
q:after {
  content: '';
  content: none;
}

table {
  border-collapse: collapse;
  border-spacing: 0;
}

/* particleground demo */
* {
  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
}

html,
body {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

body {
  background: #0074d9;
  font-family: 'Montserrat', sans-serif;
  color: #fff;
  line-height: 1.3;
  -webkit-font-smoothing: antialiased;
}

#particles {
  background: url('http://arnaudel.perso.neuf.fr/Payekhali/Fonds/1280/AS11-40-5873.jpg') top center;
  background-size: cover;
  background-repeat: no-repeat;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

#intro {
  position: absolute;
  left: 0;
  top: 50%;
  padding: 0 20px;
  width: 100%;
  text-align: center;
}

.overlay {
  position: fixed;
  background: rgba(0, 0, 0, 0.5);
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: block;
}

h1 {
  text-transform: uppercase;
  font-size: 85px;
  font-weight: 700;
  letter-spacing: 0.015em;
}

h1::after {
  content: '';
  width: 80px;
  display: block;
  background: #fff;
  height: 10px;
  margin: 30px auto;
  line-height: 1.1;
}

p {
  margin: 0 0 30px 0;
  font-size: 24px;
}

.btn {
  display: inline-block;
  padding: 15px 30px;
  border: 2px solid #fff;
  text-transform: uppercase;
  letter-spacing: 0.015em;
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
  color: #fff;
  text-decoration: none;
  -webkit-transition: all 0.4s;
  -moz-transition: all 0.4s;
  -o-transition: all 0.4s;
  transition: all 0.4s;
}

.btn:hover {
  color: #005544;
  border-color: #005544;
}

@media only screen and (max-width: 1000px) {
  h1 {
    font-size: 70px;
  }
}

@media only screen and (max-width: 800px) {
  h1 {
    font-size: 48px;
  }

  h1::after {
    height: 8px;
  }
}

@media only screen and (max-width: 568px) {
  #intro {
    padding: 0 10px;
  }

  h1 {
    font-size: 30px;
  }

  h1::after {
    height: 6px;
  }

  p {
    font-size: 18px;
  }

  .btn {
    font-size: 16px;
  }
}

@media only screen and (max-width: 320px) {
  h1 {
    font-size: 28px;
  }

  h1::after {
    height: 4px;
  }
}
</style>


```