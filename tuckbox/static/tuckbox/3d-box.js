let materials = [
    new THREE.MeshLambertMaterial({color: 0x000000, side: THREE.BackSide}),
    new THREE.MeshLambertMaterial({color: 0x00FF00, side: THREE.FrontSide}), // front
    new THREE.MeshLambertMaterial({color: 0xff0000, side: THREE.FrontSide}), // back
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // left
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // right
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // top
    new THREE.MeshLambertMaterial({side: THREE.FrontSide}), // bottom
]

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

    var ambient_light = new THREE.AmbientLight(0xC0C0C0); // soft white light
    scene.add(ambient_light);

    var light = new THREE.PointLight(0xA0A0A0);
    light.position.set(5, 5, 0);
    scene.add(light);

    var group = new THREE.Group();
    group.scale.set(1, 1, 1);
    scene.add(group)

    // front
    let front_planeGeom = new THREE.PlaneGeometry(tuckbox.width, tuckbox.height);
    front_planeGeom.translate(0, 0, tuckbox.depth / 2);
    let front_plane = new THREE.Mesh(front_planeGeom, materials[0]);
    let front_plane2 = new THREE.Mesh(front_planeGeom, materials[1]);
    group.add(front_plane);
    group.add(front_plane2);

    // back
    let back_planeGeom = new THREE.PlaneGeometry(tuckbox.width, tuckbox.height);
    back_planeGeom.rotateY(Math.PI);
    back_planeGeom.translate(0, 0, -tuckbox.depth / 2);
    let back_plane = new THREE.Mesh(back_planeGeom, materials[0]);
    let back_plane2 = new THREE.Mesh(back_planeGeom, materials[2]);
    group.add(back_plane);
    group.add(back_plane2);

    // left
    let left_planeGeom = new THREE.PlaneGeometry(tuckbox.depth, tuckbox.height);
    left_planeGeom.rotateY(-Math.PI * 0.5);
    left_planeGeom.translate(-tuckbox.width / 2, 0, 0);
    let left_plane = new THREE.Mesh(left_planeGeom, materials[0]);
    let left_plane2 = new THREE.Mesh(left_planeGeom, materials[3]);
    group.add(left_plane);
    group.add(left_plane2);

    // right
    let right_planeGeom = new THREE.PlaneGeometry(tuckbox.depth, tuckbox.height);
    right_planeGeom.rotateY(Math.PI * 0.5);
    right_planeGeom.translate(tuckbox.width / 2, 0, 0);
    let right_plane = new THREE.Mesh(right_planeGeom, materials[0]);
    let right_plane2 = new THREE.Mesh(right_planeGeom, materials[4]);
    group.add(right_plane);
    group.add(right_plane2);

    // top
    let top_planeGeom = new THREE.PlaneGeometry(tuckbox.width, tuckbox.depth);
    top_planeGeom.rotateX(-Math.PI * 0.25);
    top_planeGeom.translate(0, tuckbox.height / 2 + tuckbox.depth * Math.sin(Math.PI * 0.25) / 2, (1 - Math.cos(Math.PI * 0.25)) * tuckbox.depth / 2);
    let top_plane = new THREE.Mesh(top_planeGeom, materials[0]);
    let top_plane2 = new THREE.Mesh(top_planeGeom, materials[5]);
    group.add(top_plane);
    group.add(top_plane2);

    // bottom
    let bottom_planeGeom = new THREE.PlaneGeometry(tuckbox.width, tuckbox.depth);
    bottom_planeGeom.rotateX(Math.PI * 0.5);
    bottom_planeGeom.translate(0, -tuckbox.height / 2, 0);
    let bottom_plane = new THREE.Mesh(bottom_planeGeom, materials[0]);
    let bottom_plane2 = new THREE.Mesh(bottom_planeGeom, materials[6]);
    group.add(bottom_plane);
    group.add(bottom_plane2);

    let scaling = 3 / Math.max(tuckbox.depth, tuckbox.width, tuckbox.height)
    group.scale.set(scaling, scaling, scaling)

    window.scene = scene;
    window.THREE = THREE;

    // updating materials later works...
    materials[1].color = new THREE.Color(0x00FFFF);

    animate();

    function animate() {

        requestAnimationFrame(animate);

        renderer.render(scene, camera);

    }
}

//draw_3d_box($("body"), {"width":2, "height":3, "depth":1});
