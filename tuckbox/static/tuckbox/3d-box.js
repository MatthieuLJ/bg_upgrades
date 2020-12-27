let materials = [
    new THREE.MeshLambertMaterial({color: 0x000000, side: THREE.BackSide}),
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // front
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // back
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // left
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // right
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // top
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // bottom
]

let textures = Array(7)
let colors = Array(7)
let use_colors = Array(7).fill(false) // true if using colors, false if using pictures  (by default)
let face_rotations = Array(7).fill(0);

function draw_3d_box(container, data) {
    let tuckbox = data.tuckbox;

    let scene = new THREE.Scene();
    let camera = new THREE.PerspectiveCamera(45, 1, 0.1, 300);
    camera.position.set(6, 6, 8);

    let renderer = new THREE.WebGLRenderer({
        antialias: true
    });
    renderer.setSize(container.width(), container.width());
    container.empty();
    container.append(renderer.domElement);

    //var axesHelper = new THREE.AxesHelper(5);
    //scene.add(axesHelper);

    var controls = new THREE.OrbitControls( camera, renderer.domElement );

    scene.background = new THREE.Color(0x808080)

    var ambient_light = new THREE.AmbientLight(0x909090); // soft white light
    scene.add(ambient_light);

    var spotlight = new THREE.PointLight(0xA0A0A0);
    spotlight.position.set(5, 5, 0);
    scene.add(spotlight);

    let group = new THREE.Group();
    group.scale.set(1, 1, 1);
    scene.add(group)

    function create_plane(sizeX, sizeY, rotateX, rotateY, translateX, translateY, translateZ, material_index) {
        let planeGeom = new THREE.PlaneGeometry(sizeX, sizeY);
        if (rotateX != 0) {
            planeGeom.rotateX(rotateX);
        }
        if (rotateY != 0)  {
            planeGeom.rotateY(rotateY);
        }
        planeGeom.translate(translateX, translateY, translateZ);
        let front_plane = new THREE.Mesh(planeGeom, materials[0]);
        let back_plane = new THREE.Mesh(planeGeom, materials[material_index]);
        group.add(front_plane);
        group.add(back_plane);
    }

    create_plane(tuckbox.width, tuckbox.height, 0, 0, 0, 0, tuckbox.depth/2, 1);
    create_plane(tuckbox.width, tuckbox.height, 0, Math.PI, 0, 0,-tuckbox.depth / 2, 2);
    create_plane(tuckbox.depth, tuckbox.height, 0, -Math.PI / 2, -tuckbox.width / 2, 0, 0, 3);
    create_plane(tuckbox.depth, tuckbox.height, 0, Math.PI / 2, tuckbox.width / 2, 0, 0, 4);
    create_plane(tuckbox.width, tuckbox.depth, -Math.PI / 4, 0, 0, tuckbox.height / 2 + tuckbox.depth * Math.sin(Math.PI * 0.25) / 2, (1 - Math.cos(Math.PI * 0.25)) * tuckbox.depth / 2, 5);
    create_plane(tuckbox.width, tuckbox.depth, Math.PI / 2, 0, 0, -tuckbox.height / 2, 0, 6);

    let scaling = 3 / Math.max(tuckbox.depth, tuckbox.width, tuckbox.height)
    group.scale.set(scaling, scaling, scaling)

    window.scene = scene;
    window.THREE = THREE;

    animate();

    function animate() {

        requestAnimationFrame(animate);
        let v = new THREE.Vector3();
        camera.getWorldPosition(v);
        spotlight.position.copy(v);
        renderer.render(scene, camera);

    }
}

// face is an index: 1=front, 2=back, 3=left, 4=right, 5=top, 6=bottom
function rotate_face_image(rotation, face) {
    face_rotations[face]=rotation;
}

function set_face_usage(use_color, face) {
    use_colors[face] = use_color;
    if (use_color) {
        materials[face].map = null;
        if (colors[face]) {
            materials[face].color = colors[face];
            materials[face].needsUpdate = true;
        }
    } else {
        materials[face].color = new THREE.Color(0xffffff);
        if (textures[face]) {
            materials[face].map = textures[face];
            materials[face].needsUpdate = true;
        }
    }
}

function load_face_color(color, face) {
    colors[face] = new THREE.Color(color);
    if (use_colors[face]) {
        materials[face].color = colors[face];
        materials[face].needsUpdate = true;
    }
}

// face is an index: 1=front, 2=back, 3=left, 4=right, 5=top, 6=bottom
function load_face_image(file, face) {
    let reader = new FileReader();
    reader.onload = function(e) {
        let loader = new THREE.TextureLoader();
        loader.load(e.target.result,
            onLoad = function(tx) {
                textures[face] = tx;
                materials[face].map.center.x = 0.5;
                materials[face].map.center.y = 0.5;
                materials[face].map.rotation = - face_rotations[face] * Math.PI / 2;
                materials[face].needsUpdate = true;
                if (!use_colors[face]) {
                    materials[face].map = tx;
                }
            });
    }
    reader.readAsDataURL(file);
}

function clear_face_image(face) {
    materials[face].map = null;
    materials[face].needsUpdate = true;
}