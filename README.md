```json
{
  "chrome.exe start up":{
    "prefix": "chrome.exe",
    "body": "chrome.exe --remote-debugging-port=8899 --user-data-dir=\"D:\\playwright_chrome_data\""
  },
  "django get client ip addr":{
    "prefix": "django get client ip addr",
    "body": [
      "ip = (",
      "request.META.get(\"HTTP_X_FORWARDED_FOR\")",
      "if request.META.get(\"HTTP_X_FORWARDED_FOR\") is not None",
      "else request.META.get(\"REMOTE_ADDR\")",
      ")"
    ]
  },
  "init three scene":{
    "prefix": "three scene",
    "body": "const scene = new THREE.Scene()",
  },
  "init three gui":{
    "prefix": "three gui",
    "body": "const gui = new dat.GUI()",
  },
 "init three lights":{
    "prefix": "three lights",
    "body": [
      "const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);",
      "scene.add(ambientLight);",
      "",
      "const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);",
      "directionalLight.castShadow = true;",
      "directionalLight.shadow.mapSize.set(1024, 1024);",
      "directionalLight.shadow.camera.far = 15;",
      "directionalLight.shadow.camera.left = -7;",
      "directionalLight.shadow.camera.top = 7;",
      "directionalLight.shadow.camera.right = 7;",
      "directionalLight.shadow.camera.bottom = -7;",
      "directionalLight.position.set(5, 5, 5);",
      "scene.add(directionalLight);",
    ],
  },
  "init three sizes":{
    "prefix": "three sizes",
    "body": [
      "const sizes = {",
      "width: window.innerWidth,",
      "height: window.innerHeight,",
      "};",
    ]
  },
  "init three camera":{
    "prefix": "three camera",
    "body": [
      "const camera = new THREE.PerspectiveCamera(",
      "75,",
      "sizes.width / sizes.height,",
      " 0.1,",
      "100",
      ");",
      "camera.position.set(2, 2, 2);",
      "scene.add(camera);",
    ]
  },
  "init three AxesHelper":{
    "prefix": "three AxesHelper",
    "body":[
      "const helper = new THREE.AxesHelper();",
      "scene.add(helper);",
    ]
  },
  "init three Controls":{
    "prefix": "three Controls",
    "body": [
      "const controls = new OrbitControls(camera, canvas.current!);",
      "controls.target.set(0, 0.75, 0);",
      "controls.enableDamping = true;",
    ]
  },
  "init three Renderer":{
    "prefix": "three Renderer",
    "body": [
      "const renderer = new THREE.WebGLRenderer({",
      "canvas: canvas.current!,",
      "});",
      "renderer.shadowMap.enabled = true;",
      "renderer.shadowMap.type = THREE.PCFSoftShadowMap;",
      "renderer.setSize(sizes.width, sizes.height);",
      "renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));",
    ]
  },
  "init three Animate":{
    "prefix": "three Animate",
    "body": [
      "const clock = new THREE.Clock();",
      "let previousTime = 0;",
      "",
      "const tick = () => {",
        "const elapsedTime = clock.getElapsedTime();",
        "const deltaTime = elapsedTime - previousTime;",
        "previousTime = elapsedTime;",
        "",
        "\/\/ Update controls",
        "controls.update();",
        "",
        "\/\/ Render",
        "renderer.render(scene, camera);",
        "",
        "\/\/ Call tick again on the next frame",
        "window.requestAnimationFrame(tick);",
      "};",
        "",
      "tick();",
    ]
  },
  "init three Floor":{
    "prefix": "three Floor",
    "body": [
      "const floor = new THREE.Mesh(",
      "new THREE.PlaneGeometry(10, 10),",
      "new THREE.MeshStandardMaterial({",
      "color: \"#777777\",",    
      "metalness: 0.3,",
      "roughness: 0.4,",   
      "envMap: environmentMapTexture",
      "envMapIntensity: 0.5,",
      "})",
      ");",
      "floor.receiveShadow = true;",
      "floor.rotateX(-0.5 * Math.PI);",
      "scene.add(floor);",
    ]
  },
  "init three resizeHandler":{
    "prefix": "three resize handler",
    "body": [
      "const resizeHandler = () => {",  
      "  \/\/ Update sizes",
      "  sizes.width = window.innerWidth;",
      "  sizes.height = window.innerHeight;",
      "",
      "  \/\/ Update camera",
      "  camera.aspect = sizes.width / sizes.height;",
      "  camera.updateProjectionMatrix();",
      "",
      "  \/\/ Update renderer",
      "  renderer.setSize(sizes.width, sizes.height);",
      "  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));",  
      "};",
    ]
  },
  "init three raycaster":{
    "prefix": "three raycaster",
    "body": [
      "const raycaster = new THREE.Raycaster();",
      "const rayOrigin = new THREE.Vector3(-3, 0, 0);",
      "const rayDirection = new THREE.Vector3(1, 0, 0);",
      "rayDirection.normalize();",
      "raycaster.set(rayOrigin, rayDirection);",
      "raycaster.setFromCamera(mouse, camera)",
    ]
  },
  "init three mouse":{
    "prefix": "three mouse",
    "body": [
      "const mouse = new THREE.Vector2();",
      "window.addEventListener('mousemove', (e) => {",
      "mouse.x = (e.clientX / sizes.width) * 2 - 1;",
      "mouse.y = -(e.clientY / sizes.height) * 2 + 1;",
      "});",
    ]
  },
  "init three gltf loader":{
    "prefix": "three gltfLoader",
    "body": [
      "import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';",
      "import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';",
      "const dracoLoader = new DRACOLoader();",
      "dracoLoader.setDecoderPath('/draco/');",
      "",
      "const gltfLoader = new GLTFLoader();",
      "gltfLoader.setDRACOLoader(dracoLoader);",
      "",
      "gltfLoader.load(",
      "'/models/Fox/glTF/Fox.gltf',",
      "(gltf) => {",
      "mixer.current = new THREE.AnimationMixer(gltf.scene);",
      "  const action = mixer.current.clipAction(gltf.animations[2]);",
      "  action.play();",
      "",
      "  gltf.scene.scale.set(0.025, 0.025, 0.025);",
      "  scene.add(gltf.scene);",
      "},",
      "() => {",
      "  console.log('progress');",
      "},",
      "() => {",
      "  console.log('error');",
        "}",
      ");",
    ]
  },
  "init three hit sound":{
    "prefix": "three hit sound",
    "body": [
      "/**",
      "* Sounds",
      "*/",
      "const hitSound = new Audio(\"\/sounds\/hit.mp3\");",
      "",
      "const playHitSound = (collision) => {",
      "const impactStrength = collision.contact.getImpactVelocityAlongNormal();",
      "",
      "if (impactStrength > 1.5) {",
      "hitSound.volume = Math.random();",
      "hitSound.currentTime = 0;",
      "hitSound.play();",
        "}",
      "};",
    ]
  },
  "init three texture loader":{
    "prefix": "three textureLoader",
    "body":[
      "const textureLoader = new THREE.TextureLoader();",
      "const cubeTextureLoader = new THREE.CubeTextureLoader();",
      "",
      "const environmentMapTexture = cubeTextureLoader.load([",
      "\"\/textures\/environmentMaps\/0\/px.png\"",
      "\"\/textures\/environmentMaps\/0\/nx.png\"",
      "\"\/textures\/environmentMaps\/0\/py.png\"",
      "\"\/textures\/environmentMaps\/0\/ny.png\"",
      "\"\/textures\/environmentMaps\/0\/pz.png\"",
      "\"\/textures\/environmentMaps\/0\/nz.png\"",
      "]);",
    ]
  },
  "init three CANNON physics world":{
    "prefix": "three CANNON world",
    "body": [
      "const world = new CANNON.World();",
      "world.broadphase = new CANNON.SAPBroadphase(world);",
      "world.allowSleep = true;",
      "world.gravity.set(0, -9.82, 0);",
    ]
  },
  "init three CANNON default material":{
    "prefix": "three CANNON material",
    "body": [
      "const defaultMaterial = new CANNON.Material(\"default\");",
      "const defaultContactMaterial = new CANNON.ContactMaterial(",
      "defaultMaterial,",
      "defaultMaterial,",
      "{",
      " friction: 0.1,",
      " restitution: 0.7,",
      "}",
      ");",
      "world.defaultContactMaterial = defaultContactMaterial;",
    ]
  },
  "init three CANNON floor":{
    "prefix": "three CANNON floor",
    "body": [
      "\/\/ Floor",
      "const floorShape = new CANNON.Plane();",
      "const floorBody = new CANNON.Body();",
      "floorBody.mass = 0;",
      "floorBody.addShape(floorShape);",
      "floorBody.quaternion.setFromAxisAngle(new CANNON.Vec3(-1, 0, 0), Math.PI * 0.5);",
      "world.addBody(floorBody);"
    ]
  },
  "init three CANNON update physics":{
    "prefix": "three CANNON update physics",
    "body":[
      "\/\/ Update physics",
      "world.step(1 \/ 60, deltaTime, 3);",
      "",
      "for (const object of objectsToUpdate) {",
      " object.mesh.position.copy(object.body.position);",
      " object.mesh.quaternion.copy(object.body.quaternion);",
      "}",
    ]
  },
  "init three sphere":{
    "prefix": "three create sphere",
    "body": [
      "\/\/ Create sphere",
      "const sphereGeometry = new THREE.SphereGeometry(1, 20, 20);",
      "const sphereMaterial = new THREE.MeshStandardMaterial({",
      " metalness: 0.3,",
      " roughness: 0.4,",
      " envMap: environmentMapTexture,",
      " envMapIntensity: 0.5,",
      "});",
      "const mesh = new THREE.Mesh(sphereGeometry, sphereMaterial);",
      "mesh.castShadow = true;",
      "mesh.scale.set(radius, radius, radius);",
      "mesh.position.copy(position);",
      "scene.add(mesh);"
    ]
  },
  "init three box":{
    "prefix": "three create box",
    "body": [
      "const boxGeometry = new THREE.BoxGeometry(1, 1, 1);",
      "const boxMaterial = new THREE.MeshStandardMaterial({",
      "metalness: 0.3,",
      "roughness: 0.4,",
      "envMap: environmentMapTexture,",
      "envMapIntensity: 0.5,",
      "});",
      "const mesh = new THREE.Mesh(boxGeometry, boxMaterial);",
      "mesh.scale.set(width, height, depth);",
      "mesh.castShadow = true;",
      "mesh.position.copy(position);",
      "scene.add(mesh);",
    ]
  },
  "init three CANNON sphere":{
    "prefix": "three create CANNON sphere",
    "body": [
      "\/\/ Cannon.js body",
      "const shape = new CANNON.Sphere(radius);",
      "",
      "const body = new CANNON.Body({",
      "mass: 1,",
      "position: new CANNON.Vec3(0, 3, 0),",
      "shape: shape,",
      "material: defaultMaterial,",
      "});",
      "body.position.copy(position);",
      "body.addEventListener(\"collide\", playHitSound);",
      "world.addBody(body);",
      "",
      "\/\/ Save in objects",
      "objectsToUpdate.push({ mesh, body });"
    ]
  },
  "init three CANNON box":{
    "prefix": "three create CANNON box",
    "body": [
      "\/\/ Cannon.js body",
      "const shape = new CANNON.Box(",
      "new CANNON.Vec3(width * 0.5, height * 0.5, depth * 0.5)",
      ");",
      "",
      "const body = new CANNON.Body({",
      "mass: 1,",
      "position: new CANNON.Vec3(0, 3, 0),",
      "shape: shape,",
      "material: defaultMaterial,",
      "});",
      "body.position.copy(position);",
      "body.addEventListener(\"collide\", playHitSound);",
      "world.addBody(body);",
      "",
      "\/\/ Save in objects",
      "objectsToUpdate.push({ mesh, body });",
    ]
  }
}
```