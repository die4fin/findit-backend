import * as cheerio from 'cheerio';
import fs from 'fs';
import path from 'path';

const baseUrl = 'https://mobile-legends.fandom.com';
const listUrl = `${baseUrl}/wiki/List_of_heroes`;
const downloadDir = './mlbb_heroes_hd';

// Helper delay agar kita tidak diblokir (rate-limit) oleh server Fandom karena request terlalu cepat
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

async function downloadHighResHeroes() {
  if (!fs.existsSync(downloadDir)) {
    fs.mkdirSync(downloadDir);
  }

  console.log('1. Mengumpulkan daftar link hero dari halaman utama...');
  
  try {
    const response = await fetch(listUrl);
    const html = await response.text();
    const $ = cheerio.load(html);

    const heroPaths = new Set<string>();

    // Mencari link di dalam tabel daftar hero
    $('table tbody tr').each((_, el) => {
      // Mengambil tag <a> pertama yang ada di dalam baris tabel
      const link = $(el).find('td a').first();
      const href = link.attr('href');
      
      // Filter khusus untuk URL yang mengarah ke halaman wiki (bukan file/kategori)
      if (href && href.startsWith('/wiki/') && !href.includes(':')) {
        heroPaths.add(href);
      }
    });

    const heroes = Array.from(heroPaths);
    console.log(`[OK] Ditemukan ${heroes.length} hero.\n2. Memulai proses download gambar statis dari detail page...\n`);

    let count = 0;

    for (const heroPath of heroes) {
      const heroName = heroPath.replace('/wiki/', '').replace(/_/g, ' ');
      const heroUrl = `${baseUrl}${heroPath}`;
      
      console.log(`-> Mengakses: ${heroName}...`);
      
      try {
        const detailRes = await fetch(heroUrl);
        const detailHtml = await detailRes.text();
        const $detail = cheerio.load(detailHtml);

        // Di Fandom, gambar utama hero selalu diletakkan di dalam kotak "Aside" (Infobox)
        const imgElement = $detail('aside.portable-infobox figure.pi-image img').first();
        let imgSrc = imgElement.attr('src') || imgElement.attr('data-src');

        if (imgSrc && imgSrc.startsWith('http')) {
          // Bersihkan parameter '/revision/...' Fandom untuk mendapatkan resolusi HD aslinya
          const cleanUrl = imgSrc.split('/revision/')[0];
          const ext = path.extname(new URL(cleanUrl).pathname) || '.png';
          
          const safeName = heroName.replace(/[^a-zA-Z0-9]/g, '_');
          const filename = path.join(downloadDir, `${safeName}${ext}`);

          const imgFetchRes = await fetch(cleanUrl);
          const buffer = await imgFetchRes.arrayBuffer();

          fs.writeFileSync(filename, Buffer.from(buffer));
          console.log(`   [+] Tersimpan: ${safeName}${ext}`);
          count++;
        } else {
          console.log(`   [-] Gambar statis tidak ditemukan untuk ${heroName}`);
        }

        // Jeda 300ms agar koneksi tidak diputus paksa oleh server target
        await delay(300);

      } catch (heroErr) {
        console.error(`   [!] Gagal memproses ${heroName}:`, heroErr);
      }
    }

    console.log(`\nSelesai! Total ${count} gambar statis hero (HD) berhasil didownload.`);
    console.log(`Silakan cek folder: ${path.resolve(downloadDir)}`);
    
  } catch (error) {
    console.error('Terjadi kesalahan utama:', error);
  }
}

downloadHighResHeroes();
