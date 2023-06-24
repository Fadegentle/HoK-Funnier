use actix_files::{Files, NamedFile};
use actix_web::{get, web, App, HttpResponse, HttpServer};
use rand::seq::SliceRandom;
use std::fs;
use std::io::Read;
use std::path::PathBuf;

fn get_image_paths(folder_path: &str) -> Vec<PathBuf> {
    let mut image_paths = Vec::new();

    if let Ok(entries) = fs::read_dir(folder_path) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() && path.extension().map(|ext| ext == "jpg").unwrap_or(false) {
                image_paths.push(path);
            } else if path.is_dir() {
                image_paths.extend(get_image_paths(&path.to_string_lossy()));
            }
        }
    }

    image_paths
}

#[get("/random/hero/image")]
async fn random_hero_image() -> HttpResponse {
    // 从某个文件夹中获取所有图片文件路径
    let image_folder = "../heroes";
    let image_paths = get_image_paths(image_folder);

    // 随机选择一个图片路径
    let random_image_path = image_paths
        .choose(&mut rand::thread_rng())
        .unwrap_or(&PathBuf::from("default_image.jpg"))
        .to_owned();

    // 读取图片数据
    let mut img = fs::File::open(random_image_path).expect("图片打开失败");
    let mut buffer = Vec::new();
    if img.read_to_end(&mut buffer).is_err() {
        return HttpResponse::InternalServerError().body("图片读取失败");
    }

    println!("{:?}", img);
    // 返回随机图片的数据
    HttpResponse::Ok().content_type("image/jpeg").body(buffer)
}

#[get("/random/hero")]
async fn random_hero() -> actix_web::Result<NamedFile> {
    Ok(NamedFile::open("./asset/random_hero.html")?)
}

#[get("/")]
async fn index() -> actix_web::Result<NamedFile> {
    Ok(NamedFile::open("./asset/index.html")?)
}

#[get("/favicon.ico")]
async fn favicon() -> actix_web::Result<NamedFile> {
    Ok(NamedFile::open("./asset/favicon.ico")?)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(favicon)
            .service(index)
            .service(random_hero)
            .service(random_hero_image)
            .default_service(web::route().to(HttpResponse::NotFound))
            .service(Files::new("/", "./asset"))
    })
    .bind("0.0.0.0:8000")?
    .run()
    .await
}
