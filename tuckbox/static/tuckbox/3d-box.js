function draw_3d_box(container, data) {
    let tuckbox = data.tuckbox;

    let scene = new THREE.Scene();
    let camera = new THREE.PerspectiveCamera(45, 1, 0.1, 300);
    camera.position.set(0, 0, 10);

    let renderer = new THREE.WebGLRenderer({
        antialias: true
    });
    renderer.setSize(container.width(), container.width());
    container.empty();
    container.append(renderer.domElement);

    var axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);

    //var controls = new THREE.OrbitControls(camera, renderer.domElement);

    var ambient_light = new THREE.AmbientLight(0x606060); // soft white light
    scene.add(ambient_light);

    var light = new THREE.PointLight(0xFFFFFF);
    light.position.set(5, 5, 0);
    scene.add(light);

    var group = new THREE.Group();
    group.scale.set(1, 1, 1);
    scene.add(group)

    materials = [
        new THREE.MeshLambertMaterial({color: 0x000000, side: THREE.BackSide}),
        new THREE.MeshLambertMaterial({color: 0xFF0000, side: THREE.FrontSide}),
        new THREE.MeshLambertMaterial({color: 0x00FF00, side: THREE.FrontSide}),
        new THREE.MeshLambertMaterial({color: 0x0000FF, side: THREE.FrontSide})
    ]

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
    let back_plane2 = new THREE.Mesh(back_planeGeom, materials[1]);
    group.add(back_plane);
    group.add(back_plane2);

    // right
    let right_planeGeom = new THREE.PlaneGeometry(tuckbox.depth, tuckbox.height);
    right_planeGeom.rotateY(Math.PI * 0.5);
    right_planeGeom.translate(tuckbox.width / 2, 0, 0);
    let right_plane = new THREE.Mesh(right_planeGeom, materials[0]);
    let right_plane2 = new THREE.Mesh(right_planeGeom, materials[2]);
    group.add(right_plane);
    group.add(right_plane2);

    // left
    let left_planeGeom = new THREE.PlaneGeometry(tuckbox.depth, tuckbox.height);
    left_planeGeom.rotateY(-Math.PI * 0.5);
    left_planeGeom.translate(-tuckbox.width / 2, 0, 0);
    let left_plane = new THREE.Mesh(left_planeGeom, materials[0]);
    let left_plane2 = new THREE.Mesh(left_planeGeom, materials[2]);
    group.add(left_plane);
    group.add(left_plane2);

    // bottom
    let bottom_planeGeom = new THREE.PlaneGeometry(tuckbox.width, tuckbox.depth);
    bottom_planeGeom.rotateX(Math.PI * 0.5);
    bottom_planeGeom.translate(0, -tuckbox.height / 2, 0);
    let bottom_plane = new THREE.Mesh(bottom_planeGeom, materials[0]);
    let bottom_plane2 = new THREE.Mesh(bottom_planeGeom, materials[3]);
    group.add(bottom_plane);
    group.add(bottom_plane2);


    /*
     * var gui = new dat.GUI();
     * gui.add(group.scale, "x", 0.1, 5);
     * gui.add(group.scale, "y", 0.1, 5);
     * gui.add(group.scale, "z", 0.1, 5);
     * */

    window.scene = scene;
    window.THREE = THREE;

    animate();

    function animate() {

        requestAnimationFrame(animate);

        group.rotation.x += 0.01;
        group.rotation.y += 0.005;

        renderer.render(scene, camera);

    }
}

//draw_3d_box($("body"), {"width":2, "height":3, "depth":1});
