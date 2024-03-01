import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let materials = [
    new THREE.MeshLambertMaterial({color: 0xffffff, side: THREE.BackSide}),
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
let bottom_geometry;
let is_open = false;
let tuckbox;

function draw_3d_box(container, data) {
    tuckbox = data.tuckbox;

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

    var controls = new OrbitControls( camera, renderer.domElement );

    scene.background = new THREE.Color(0xFFFFFF)

    var ambient_light = new THREE.AmbientLight(0xA0A0A0); // soft white light
    scene.add(ambient_light);

    var pointlight = new THREE.PointLight(0xFFFFFF);
    pointlight.position.set(2, 2, 0);
    pointlight.decay = 0.45;
    pointlight.power = 80;
    scene.add(pointlight);

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

        return planeGeom;
    }

    create_plane(tuckbox.width, tuckbox.height, 0, 0, 0, 0, tuckbox.depth/2, 1);
    create_plane(tuckbox.width, tuckbox.height, 0, Math.PI, 0, 0,-tuckbox.depth / 2, 2);
    create_plane(tuckbox.depth, tuckbox.height, 0, -Math.PI / 2, -tuckbox.width / 2, 0, 0, 3);
    create_plane(tuckbox.depth, tuckbox.height, 0, Math.PI / 2, tuckbox.width / 2, 0, 0, 4);
    create_plane(tuckbox.width, tuckbox.depth, -Math.PI / 4, 0, 0, tuckbox.height / 2 + tuckbox.depth * Math.sin(Math.PI / 4) / 2, (1 - Math.cos(Math.PI / 4)) * tuckbox.depth / 2, 5);
    bottom_geometry = create_plane(tuckbox.width, tuckbox.depth, Math.PI / 2, 0, 0, -tuckbox.height / 2, 0, 6);

    let scaling = 3 / Math.max(tuckbox.depth, tuckbox.width, tuckbox.height)
    group.scale.set(scaling, scaling, scaling)

    window.scene = scene;
    window.THREE = THREE;

    animate();

    function animate() {

        requestAnimationFrame(animate);
        let v = new THREE.Vector3();
        camera.getWorldPosition(v);
        pointlight.position.copy(v);
        renderer.render(scene, camera);
    }
}

function open_bottom(open) {
    if (open == is_open) {
        // nothing to do here
        return;
    }
    if (open) {
        bottom_geometry.translate(0, tuckbox.height / 2, 0);
        bottom_geometry.rotateX(-Math.PI / 4);
        bottom_geometry.translate(0, -tuckbox.height / 2 - tuckbox.depth * Math.sin(Math.PI / 4) / 2, (1 - Math.cos(Math.PI / 4)) * tuckbox.depth / 2);
    } else {
        bottom_geometry.translate(0, tuckbox.height / 2 + tuckbox.depth * Math.sin(Math.PI / 4) / 2, (Math.cos(Math.PI / 4) - 1) * tuckbox.depth / 2);
        bottom_geometry.rotateX(Math.PI / 4);
        bottom_geometry.translate(0, -tuckbox.height / 2, 0);
    }
    is_open = open;
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
        }
    } else {
        materials[face].color = new THREE.Color(0xffffff);
        if (textures[face]) {
            materials[face].map = textures[face];
            materials[face].map.center.x = 0.5;
            materials[face].map.center.y = 0.5;
            materials[face].map.rotation = - face_rotations[face] * Math.PI / 2;
        }
    }
    materials[face].needsUpdate = true;
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
            function(tx) {
                textures[face] = tx;
                materials[face].needsUpdate = true;
                if (!use_colors[face]) {
                    materials[face].map = tx;
                    materials[face].map.center.x = 0.5;
                    materials[face].map.center.y = 0.5;
                    materials[face].map.rotation = - face_rotations[face] * Math.PI / 2;
                }
            });
    }
    reader.readAsDataURL(file);
}

function clear_face_image(face) {
    materials[face].map = null;
    materials[face].needsUpdate = true;
}

export { draw_3d_box, open_bottom, rotate_face_image, set_face_usage, load_face_color, load_face_image, clear_face_image };
