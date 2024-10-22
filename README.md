```html
<h1 class="title">Hover over the cards</h1>

<div id="app" class="container">
  <card data-image="https://images.unsplash.com/photo-1479660656269-197ebb83b540?dpr=2&auto=compress,format&fit=crop&w=1199&h=798&q=80&cs=tinysrgb&crop=">
    <h1 slot="header">Canyons</h1>
    <p slot="content">Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
  </card>
  <card data-image="https://images.unsplash.com/photo-1479659929431-4342107adfc1?dpr=2&auto=compress,format&fit=crop&w=1199&h=799&q=80&cs=tinysrgb&crop=">
    <h1 slot="header">Beaches</h1>
    <p slot="content">Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
  </card>
  <card data-image="https://images.unsplash.com/photo-1479644025832-60dabb8be2a1?dpr=2&auto=compress,format&fit=crop&w=1199&h=799&q=80&cs=tinysrgb&crop=">
    <h1 slot="header">Trees</h1>
    <p slot="content">Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
  </card>
  <card data-image="https://images.unsplash.com/photo-1479621051492-5a6f9bd9e51a?dpr=2&auto=compress,format&fit=crop&w=1199&h=811&q=80&cs=tinysrgb&crop=">
    <h1 slot="header">Lakes</h1>
    <p slot="content">Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>
  </card>
</div>
```

```css
$hoverEasing: cubic-bezier(0.23, 1, 0.32, 1);
$returnEasing: cubic-bezier(0.445, 0.05, 0.55, 0.95);

body {
  margin: 40px 0;
  font-family: "Raleway";
  font-size: 14px;
  font-weight: 500;
  background-color: #BCAAA4;
  -webkit-font-smoothing: antialiased;
}

.title {
  font-family: "Raleway";
  font-size: 24px;
  font-weight: 700;
  color: #5D4037;
  text-align: center;
}

p {
  line-height: 1.5em;
}

h1+p, p+p {
  margin-top: 10px;
}

.container {
  padding: 40px 80px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.card-wrap {
  margin: 10px;
  transform: perspective(800px);
  transform-style: preserve-3d;
  cursor: pointer;
  // background-color: #fff;
  
  &:hover {
    .card-info {
      transform: translateY(0);
    }
    .card-info p {
      opacity: 1;
    }
    .card-info, .card-info p {
      transition: 0.6s $hoverEasing;
    }
    .card-info:after {
      transition: 5s $hoverEasing;
      opacity: 1;
      transform: translateY(0);
    }
    .card-bg {
      transition: 
        0.6s $hoverEasing,
        opacity 5s $hoverEasing;
      opacity: 0.8;
    }
    .card {
      transition:
        0.6s $hoverEasing,
        box-shadow 2s $hoverEasing;
      box-shadow:
        rgba(white, 0.2) 0 0 40px 5px,
        rgba(white, 1) 0 0 0 1px,
        rgba(black, 0.66) 0 30px 60px 0,
        inset #333 0 0 0 5px,
        inset white 0 0 0 6px;
    }
  }
}

.card {
  position: relative;
  flex: 0 0 240px;
  width: 240px;
  height: 320px;
  background-color: #333;
  overflow: hidden;
  border-radius: 10px;
  box-shadow:
    rgba(black, 0.66) 0 30px 60px 0,
    inset #333 0 0 0 5px,
    inset rgba(white, 0.5) 0 0 0 6px;
  transition: 1s $returnEasing;
}

.card-bg {
  opacity: 0.5;
  position: absolute;
  top: -20px; left: -20px;
  width: 100%;
  height: 100%;
  padding: 20px;
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;
  transition:
    1s $returnEasing,
    opacity 5s 1s $returnEasing;
  pointer-events: none;
}

.card-info {
  padding: 20px;
  position: absolute;
  bottom: 0;
  color: #fff;
  transform: translateY(40%);
  transition: 0.6s 1.6s cubic-bezier(0.215, 0.61, 0.355, 1);
  
  p {
    opacity: 0;
    text-shadow: rgba(black, 1) 0 2px 3px;
    transition: 0.6s 1.6s cubic-bezier(0.215, 0.61, 0.355, 1);
  }
  
  * {
    position: relative;
    z-index: 1;
  }
  
  &:after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    z-index: 0;
    width: 100%;
    height: 100%;
    background-image: linear-gradient(to bottom, transparent 0%, rgba(#000, 0.6) 100%);
    background-blend-mode: overlay;
    opacity: 0;
    transform: translateY(100%);
    transition: 5s 1s $returnEasing;
  }
}

.card-info h1 {
  font-family: "Playfair Display";
  font-size: 36px;
  font-weight: 700;
  text-shadow: rgba(black, 0.5) 0 10px 10px;
}
```

```javascript
Vue.config.devtools = true;

Vue.component('card', {
  template: `
    <div class="card-wrap"
      @mousemove="handleMouseMove"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      ref="card">
      <div class="card"
        :style="cardStyle">
        <div class="card-bg" :style="[cardBgTransform, cardBgImage]"></div>
        <div class="card-info">
          <slot name="header"></slot>
          <slot name="content"></slot>
        </div>
      </div>
    </div>`,
  mounted() {
    this.width = this.$refs.card.offsetWidth;
    this.height = this.$refs.card.offsetHeight;
  },
  props: ['dataImage'],
  data: () => ({
    width: 0,
    height: 0,
    mouseX: 0,
    mouseY: 0,
    mouseLeaveDelay: null
  }),
  computed: {
    mousePX() {
      return this.mouseX / this.width;
    },
    mousePY() {
      return this.mouseY / this.height;
    },
    cardStyle() {
      const rX = this.mousePX * 30;
      const rY = this.mousePY * -30;
      return {
        transform: `rotateY(${rX}deg) rotateX(${rY}deg)`
      };
    },
    cardBgTransform() {
      const tX = this.mousePX * -40;
      const tY = this.mousePY * -40;
      return {
        transform: `translateX(${tX}px) translateY(${tY}px)`
      }
    },
    cardBgImage() {
      return {
        backgroundImage: `url(${this.dataImage})`
      }
    }
  },
  methods: {
    handleMouseMove(e) {
      this.mouseX = e.pageX - this.$refs.card.offsetLeft - this.width/2;
      this.mouseY = e.pageY - this.$refs.card.offsetTop - this.height/2;
    },
    handleMouseEnter() {
      clearTimeout(this.mouseLeaveDelay);
    },
    handleMouseLeave() {
      this.mouseLeaveDelay = setTimeout(()=>{
        this.mouseX = 0;
        this.mouseY = 0;
      }, 1000);
    }
  }
});

const app = new Vue({
  el: '#app'
});
```

```html
<!-- about -->
<div class="about">
   <a class="bg_links social portfolio" href="https://www.rafaelalucas.com" target="_blank">
      <span class="icon"></span>
   </a>
   <a class="bg_links social dribbble" href="https://dribbble.com/rafaelalucas" target="_blank">
      <span class="icon"></span>
   </a>
   <a class="bg_links social linkedin" href="https://www.linkedin.com/in/rafaelalucas/" target="_blank">
      <span class="icon"></span>
   </a>
   <a class="bg_links logo"></a>
</div>
<!-- end about -->

    <nav>
        <div class="menu">
            <p class="website_name">LOGO</p>
            <div class="menu_links">
                <a href="" class="link">about</a>
                <a href="" class="link">projects</a>
                <a href="" class="link">contacts</a>
            </div>
            <div class="menu_icon">
                <span class="icon"></span>
            </div>
        </div>
    </nav>

    <section class="wrapper">

        <div class="container">

            <div id="scene" class="scene" data-hover-only="false">


                <div class="circle" data-depth="1.2"></div>

                <div class="one" data-depth="0.9">
                    <div class="content">
                        <span class="piece"></span>
                        <span class="piece"></span>
                        <span class="piece"></span>
                    </div>
                </div>

                <div class="two" data-depth="0.60">
                    <div class="content">
                        <span class="piece"></span>
                        <span class="piece"></span>
                        <span class="piece"></span>
                    </div>
                </div>

                <div class="three" data-depth="0.40">
                    <div class="content">
                        <span class="piece"></span>
                        <span class="piece"></span>
                        <span class="piece"></span>
                    </div>
                </div>

                <p class="p404" data-depth="0.50">404</p>
                <p class="p404" data-depth="0.10">404</p>

            </div>

            <div class="text">
                <article>
                    <p>Uh oh! Looks like you got lost. <br>Go back to the homepage if you dare!</p>
                    <button>i dare!</button>
                </article>
            </div>

        </div>
    </section>
```

```css
.about {
   $cubic: cubic-bezier(0.64, 0.01, 0.07, 1.65);
   $transition: 0.6s $cubic;
   $size: 40px;
   position: fixed;
   z-index: 10;
   bottom: 10px;
   right: 10px;
   width: $size;
   height: $size;
   display: flex;
   justify-content: flex-end;
   align-items: flex-end;
   transition: all 0.2s ease;

   .bg_links {
      width: $size;
      height: $size;
      border-radius: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: rgba(#000000, 0.2);
      border-radius: 100%;
      backdrop-filter: blur(5px);
      position: absolute;
   }

   .logo {
      width: $size;
      height: $size;
      z-index: 9;
      background-image: url(https://rafaelavlucas.github.io/assets/codepen/logo_white.svg);
      background-size: 50%;
      background-repeat: no-repeat;
      background-position: 10px 7px;
      opacity: 0.9;
      transition: all 1s 0.2s ease;
      bottom: 0;
      right: 0;
   }

   .social {
      opacity: 0;
      right: 0;
      bottom: 0;

      .icon {
         width: 100%;
         height: 100%;
         background-size: 20px;
         background-repeat: no-repeat;
         background-position: center;
         background-color: transparent;
         display: flex;
         transition: all 0.2s ease, background-color 0.4s ease;
         opacity: 0;
         border-radius: 100%;
      }

      &.portfolio {
         transition: all 0.8s ease;

         .icon {
            background-image: url(https://rafaelavlucas.github.io/assets/codepen/link.svg);
         }
      }

      &.dribbble {
         transition: all 0.3s ease;
         .icon {
            background-image: url(https://rafaelavlucas.github.io/assets/codepen/dribbble.svg);
         }
      }

      &.linkedin {
         transition: all 0.8s ease;
         .icon {
            background-image: url(https://rafaelavlucas.github.io/assets/codepen/linkedin.svg);
         }
      }
   }

   &:hover {
      width: 105px;
      height: 105px;
      transition: all $transition;

      .logo {
         opacity: 1;
         transition: all 0.6s ease;
      }

      .social {
         opacity: 1;

         .icon {
            opacity: 0.9;
         }

         &:hover {
            background-size: 28px;
            .icon {
               background-size: 65%;
               opacity: 1;
            }
         }

         &.portfolio {
            right: 0;
            bottom: calc(100% - 40px);
            transition: all 0.3s 0s $cubic;
            .icon {
               &:hover {
                  background-color: #698fb7;
               }
            }
         }

         &.dribbble {
            bottom: 45%;
            right: 45%;
            transition: all 0.3s 0.15s $cubic;
            .icon {
               &:hover {
                  background-color: #ea4c89;
               }
            }
         }

         &.linkedin {
            bottom: 0;
            right: calc(100% - 40px);
            transition: all 0.3s 0.25s $cubic;
            .icon {
               &:hover {
                  background-color: #0077b5;
               }
            }
         }
      }
   }
}

@import url("https://fonts.googleapis.com/css?family=Barlow+Condensed:300,400,500,600,700,800,900|Barlow:300,400,500,600,700,800,900&display=swap");

$font-01: "Barlow",
sans-serif;
$font-02: "Barlow Condensed",
sans-serif;

$m-01: #FB8A8A;
$m-02: #FFEDC0;

$bg-01: #695681;
$bg-02: #36184F;
$bg-03: #32243E;

$g-01: linear-gradient(90deg, #FFEDC0 0%, #FF9D87 100%);
$g-02: linear-gradient(90deg, #8077EA 13.7%, #EB73FF 94.65%);

$cubic: cubic-bezier(0.4, 0.35, 0, 1.53);
$cubic2: cubic-bezier(0.18, 0.89, 0.32, 1.15);

$circleShadow: inset 5px 20px 40px rgba($bg-02, 0.25),
inset 5px 0px 5px rgba($bg-03, 0.3),
inset 5px 5px 20px rgba($bg-03, 0.25),
2px 2px 5px rgba(white, 0.2);


@mixin sm {
    @media screen and (max-width: 799px) {
        @content;
    }
}

@mixin height {
    @media screen and (max-height:660px) {
        @content;
    }
}

h1,
h2,
h3,
h4,
h5,
h6,
p,
ul,
li,
button,
a,
i,
input,
body {
    margin: 0;
    padding: 0;
    list-style: none;
    border: 0;
    -webkit-tap-highlight-color: transparent;
    text-decoration: none;
    color: inherit;

    &:focus {
        outline: 0;
    }
}


body {
    margin: 0;
    padding: 0;
    height: auto;
    font-family: $font-01;
    background: $bg-01;

}

.logo {
    position: fixed;
    z-index: 5;
    bottom: 10px;
    right: 10px;
    width: 40px;
    height: 40px;
    border-radius: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 100%;
    backdrop-filter: blur(5px);

    img {

        width: 55%;
        height: 55%;
        transform: translateY(-1px);
        opacity: 0.8;
    }
}


nav {
    .menu {
        width: 100%;
        height: 80px;
        position: absolute;
        display: flex;
        align-items: center;
        justify-content: space-between;
        //background-color: red;
        padding: 0 5%;
        box-sizing: border-box;
        z-index: 3;

        .website_name {
            color: $bg-01;
            font-weight: 600;
            font-size: 20px;
            letter-spacing: 1px;
            background: white;
            padding: 4px 8px;
            border-radius: 2px;
            opacity: 0.5;
            transition: all 0.4s ease;
            cursor: pointer;

            &:hover {
                opacity: 1;
            }
        }

        .menu_links {
            transition: all 0.4s ease;
            opacity: 0.5;

            &:hover {
                opacity: 1;
            }

            @include sm {
                display: none;

            }

            .link {
                color: white;
                text-transform: uppercase;
                font-weight: 500;
                margin-right: 50px;
                letter-spacing: 2px;
                position: relative;
                transition: all 0.3s 0.2s ease;

                &:last-child {
                    margin-right: 0;
                }

                &:before {
                    content: '';
                    position: absolute;
                    width: 0px;
                    height: 4px;
                    background: $g-01;
                    bottom: -10px;
                    border-radius: 4px;
                    transition: all 0.4s cubic-bezier(0.82, 0.02, 0.13, 1.26);
                    left: 100%;
                }

                &:hover {
                    opacity: 1;
                    color: $m-01;

                    &:before {
                        width: 40px;
                        left: 0;


                    }
                }
            }
        }

        .menu_icon {
            width: 40px;
            height: 40px;
            position: relative;
            display: none;
            justify-content: center;
            align-items: center;
            cursor: pointer;


            @include sm {
                display: flex;
            }

            .icon {
                width: 24px;
                height: 2px;
                background: white;
                position: absolute;

                &:before,
                &:after {
                    content: '';
                    width: 100%;
                    height: 100%;
                    background: inherit;
                    position: absolute;
                    transition: all 0.3s cubic-bezier(0.49, 0.04, 0, 1.55);
                }

                &:before {
                    transform: translateY(-8px);
                }

                &:after {
                    transform: translateY(8px);
                }


            }

            &:hover {
                .icon {
                    background: $m-02;

                    &:before {
                        transform: translateY(-10px);
                    }

                    &:after {
                        transform: translateY(10px);
                    }
                }
            }
        }
    }
}

.wrapper {
    display: grid;
    grid-template-columns: 1fr;
    justify-content: center;
    align-items: center;
    height: 100vh;
    overflow-x: hidden;

    .container {
        margin: 0 auto;
        transition: all 0.4s ease;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;

        // Scene for the Parallax Effect
        .scene {
            position: absolute;
            width: 100vw;
            height: 100vh;
            vertical-align: middle;
        }

        // All elements' containers
        .one,
        .two,
        .three,
        .circle,
        .p404 {
            width: 60%;
            height: 60%;
            top: 20% !important;
            left: 20% !important;
            min-width: 400px;
            min-height: 400px;

            .content {
                width: 600px;
                height: 600px;
                display: flex;
                justify-content: center;
                align-items: center;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                animation: content 0.8s cubic-bezier(1, 0.06, 0.25, 1) backwards;

                @keyframes content {
                    0% {
                        width: 0;
                    }
                }

                // Pieces
                .piece {
                    width: 200px;
                    height: 80px;
                    display: flex;
                    position: absolute;
                    border-radius: 80px;
                    z-index: 1;

                    animation: pieceLeft 8s cubic-bezier(1, 0.06, 0.25, 1) infinite both;


                    @keyframes pieceLeft {
                        0% {}

                        50% {
                            left: 80%;
                            width: 10%;
                        }

                        100% {}

                    }

                    @keyframes pieceRight {
                        0% {}

                        50% {
                            right: 80%;
                            width: 10%;
                        }

                        100% {}

                    }

                }
            }

            @include sm {
                width: 90%;
                height: 90%;
                top: 5% !important;
                left: 5% !important;
                min-width: 280px;
                min-height: 280px;
            }

            @include height {
                min-width: 280px;
                min-height: 280px;
                width: 60%;
                height: 60%;
                top: 20% !important;
                left: 20% !important;
            }
        }

        // Text and Button container
        .text {
            width: 60%;
            height: 40%;
            min-width: 400px;
            min-height: 500px;
            position: absolute;
            margin: 40px 0;
            animation: text 0.6s 1.8s ease backwards;

            @keyframes text {
                0% {
                    opacity: 0;
                    transform: translateY(40px);
                }
            }

            @include sm {
                min-height: 400px;
                height: 80%;
            }

            article {
                width: 400px;
                position: absolute;
                bottom: 0;
                z-index: 4;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%);


                @include sm {
                    width: 100%;
                }

                p {
                    color: white;
                    font-size: 18px;
                    letter-spacing: 0.6px;
                    margin-bottom: 40px;
                    text-shadow: 6px 6px 10px $bg-03;
                }

                button {
                    height: 40px;
                    padding: 0 30px;
                    border-radius: 50px;
                    cursor: pointer;
                    box-shadow: 0px 15px 20px rgba($bg-02, 0.5);
                    z-index: 3;
                    color: $bg-01;
                    background-color: white;
                    text-transform: uppercase;
                    font-weight: 600;
                    font-size: 12px;
                    transition: all 0.3s ease;


                    &:hover {
                        box-shadow: 0px 10px 10px -10px rgba($bg-02, 0.5);
                        transform: translateY(5px);
                        background: $m-01;
                        color: white;
                    }
                }
            }
        }

        // The 404 Number
        .p404 {
            font-size: 200px;
            font-weight: 700;
            letter-spacing: 4px;
            color: white;
            display: flex !important;
            justify-content: center;
            align-items: center;
            position: absolute;
            z-index: 2;
            animation: anime404 0.6s cubic-bezier(0.3, 0.8, 1, 1.05) both;
            animation-delay: 1.2s;

            @include sm {
                font-size: 100px;
            }

            @keyframes anime404 {
                0% {
                    opacity: 0;
                    transform: scale(10) skew(20deg, 20deg);
                }
            }

            &:nth-of-type(2) {
                color: $bg-02;
                z-index: 1;
                animation-delay: 1s;
                filter: blur(10px);
                opacity: 0.8;
            }


        }

        // Bigger Circle
        .circle {
            position: absolute;

            &:before {
                content: '';
                position: absolute;
                width: 800px;
                height: 800px;
                background-color: rgba($bg-02, 0.2);
                border-radius: 100%;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                box-shadow: $circleShadow;
                animation: circle 0.8s cubic-bezier(1, 0.06, 0.25, 1) backwards;


                @keyframes circle {
                    0% {
                        width: 0;
                        height: 0;
                    }
                }

                @include sm {
                    width: 400px;
                    height: 400px;
                }
            }
        }

        // Container 1
        .one {
            .content {

                // Smaller Circle
                &:before {
                    content: '';
                    position: absolute;
                    width: 600px;
                    height: 600px;
                    background-color: rgba($bg-02, 0.3);
                    border-radius: 100%;
                    box-shadow: $circleShadow;
                    animation: circle 0.8s 0.4s cubic-bezier(1, 0.06, 0.25, 1) backwards;

                    @include sm {
                        width: 300px;
                        height: 300px;
                    }
                }

                .piece {
                    background: $g-02;

                    &:nth-child(1) {
                        right: 15%;
                        top: 18%;
                        height: 30px;
                        width: 120px;
                        animation-delay: 0.5s;
                        animation-name: pieceRight;
                    }

                    &:nth-child(2) {
                        left: 15%;
                        top: 45%;
                        width: 150px;
                        height: 50px;
                        animation-delay: 1s;
                        animation-name: pieceLeft;
                    }

                    &:nth-child(3) {
                        left: 10%;
                        top: 75%;
                        height: 20px;
                        width: 70px;
                        animation-delay: 1.5s;
                        animation-name: pieceLeft;
                    }

                }


            }
        }

        // Container 2
        .two {
            .content {
                .piece {
                    background: $g-01;

                    &:nth-child(1) {
                        left: 0%;
                        top: 25%;
                        height: 40px;
                        width: 120px;
                        animation-delay: 2s;
                        animation-name: pieceLeft;
                    }

                    &:nth-child(2) {
                        right: 15%;
                        top: 35%;
                        width: 180px;
                        height: 50px;
                        animation-delay: 2.5s;
                        animation-name: pieceRight;
                    }

                    &:nth-child(3) {
                        right: 10%;
                        top: 80%;
                        height: 20px;
                        width: 160px;
                        animation-delay: 3s;
                        animation-name: pieceRight;
                    }

                }
            }
        }

        // Container 3
        .three {
            .content {
                .piece {
                    background: $m-01;

                    &:nth-child(1) {
                        left: 25%;
                        top: 35%;
                        height: 20px;
                        width: 80px;
                        animation-name: pieceLeft;
                        animation-delay: 3.5s;
                    }

                    &:nth-child(2) {
                        right: 10%;
                        top: 55%;
                        width: 140px;
                        height: 40px;
                        animation-name: pieceRight;
                        animation-delay: 4s;
                    }

                    &:nth-child(3) {
                        left: 40%;
                        top: 68%;
                        height: 20px;
                        width: 80px;
                        animation-name: pieceLeft;
                        animation-delay: 4.5s;
                    }

                }


            }
        }


    }
}

```

```javascript
        // Parallax Code
        var scene = document.getElementById('scene');
        var parallax = new Parallax(scene);
```