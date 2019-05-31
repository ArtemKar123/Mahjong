package com.example.warte.samsungfinalproject;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.service.quicksettings.Tile;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.reflect.Array;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashSet;
import java.util.Iterator;

public class MainActivity extends AppCompatActivity {

    static final int REQUEST_TAKE_PHOTO = 1;
    private String mCurrentPhotoPath;
    private ImageView imageView;
    private Uri photoURI;
    protected File file;
    protected String[] tiles;
    protected TextView text;
    Animation animAlpha;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        animAlpha = AnimationUtils.loadAnimation(this, R.anim.alpha);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


        text = findViewById(R.id.text);
        imageView = findViewById(R.id.imageView);
        imageView.setImageDrawable(getDrawable(R.drawable.img));
    }

    public void onClick(View view) {
        text.setText("Подождите, ваше фото обрабатывается");
        view.startAnimation(animAlpha);
        dispatchTakePictureIntent();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_TAKE_PHOTO && resultCode == RESULT_OK) {
            imageView.setImageURI(photoURI);
            Log.d("myTag", "1");
            new SendData().execute();
        }
    }

    private File createImageFile() throws IOException {
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        File image = File.createTempFile(
                imageFileName,  /* prefix */
                ".jpg",         /* suffix */
                storageDir      /* directory */
        );

        // Save a file: path for use with ACTION_VIEW intents
        mCurrentPhotoPath = image.getAbsolutePath();
        Log.d("myTag123", image.getAbsolutePath());
        return image;
    }

    private void dispatchTakePictureIntent() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        // Ensure that there's a camera activity to handle the intent
        if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
            // Create the File where the photo should go
            File photoFile = null;
            try {
                photoFile = createImageFile();
            } catch (IOException ex) {
                // Error occurred while creating the File
                Toast.makeText(this, "Error!", Toast.LENGTH_SHORT).show();
            }
            // Continue only if the File was successfully created
            if (photoFile != null) {
                photoURI = FileProvider.getUriForFile(this,
                        "com.example.warte.samsungfinalproject",
                        photoFile);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                startActivityForResult(takePictureIntent, REQUEST_TAKE_PHOTO);
            }
            file = photoFile;
        }
    }

    class SendData extends AsyncTask<Void, Void, Void> {
        File targetFile;
        URL connectURL;
        String responseString;
        byte[ ] dataToServer;
        FileInputStream fileInputStream = null;

        String resultString = null;

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            Log.d("myTag", "2");
            String myURL = "http://192.168.1.5:8080";
            try {
                connectURL = new URL(myURL);
            } catch (MalformedURLException e) {
                e.printStackTrace();
            }
        }

        @Override
        protected Void doInBackground(Void... params) {
            String lineEnd = "\r\n";
            String twoHyphens = "--";
            String boundary = "*****";
            try
            {
                Log.d("myTag", "3");
                fileInputStream = new FileInputStream(file);
                Log.d("myTag", "4");
                // Open a HTTP connection to the URL
                HttpURLConnection conn = (HttpURLConnection)connectURL.openConnection();
                Log.d("myTag", "5");
                Log.d("myTag123", String.valueOf(conn));
                // Allow Inputs
                conn.setDoInput(true);

                // Allow Outputs
                conn.setDoOutput(true);

                // Don't use a cached copy.
                conn.setUseCaches(false);

                // Use a post method.
                conn.setRequestMethod("POST");

                conn.setRequestProperty("Connection", "Keep-Alive");

                conn.setRequestProperty("Content-Type", "multipart/form-data;boundary="+boundary);

                Log.d("myTag123","1");

                DataOutputStream dos = new DataOutputStream(conn.getOutputStream());

                Log.d("myTag123","2");

                // create a buffer of maximum size
                int bytesAvailable = fileInputStream.available();

                int maxBufferSize = 1024;
                int bufferSize = Math.min(bytesAvailable, maxBufferSize);
                byte[ ] buffer = new byte[bufferSize];

                // read file and write it into form...
                int bytesRead = fileInputStream.read(buffer, 0, bufferSize);

                while (bytesRead > 0)
                {
                    dos.write(buffer, 0, bufferSize);
                    bytesAvailable = fileInputStream.available();
                    bufferSize = Math.min(bytesAvailable,maxBufferSize);
                    bytesRead = fileInputStream.read(buffer, 0,bufferSize);
                }
                dos.writeBytes(lineEnd);
                dos.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd);

                // close streams
                fileInputStream.close();

                dos.flush();

                InputStream is = conn.getInputStream();
                String s = "";
                int ch;
                OutputStream outStream = null;
                StringBuffer b =new StringBuffer();
                while( ( ch = is.read() ) != -1 ){
                    b.append( (char)ch );
                    s = b.toString();
                    if (s.charAt(s.length()-1) == '&'){
                        targetFile = createImageFile();
                        outStream = new FileOutputStream(targetFile);
                        byte[] bbuffer = new byte[8 * 1024];
                        int bbytesRead = ch;
                        while ((bbytesRead = is.read(bbuffer)) != -1) {
                            outStream.write(bbuffer, 0, bbytesRead);
                        }
                        break;
                    }

                }
                s = s.substring(0, s.length()-1);
                tiles = s.split(",");
            }
            catch (Exception ex)
            {}
            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            super.onPostExecute(result);
            if (targetFile != null) {
                imageView.setImageURI(Uri.parse(targetFile.getAbsolutePath()));
                Tiles a = new Tiles(tiles);
                text.setText("У вас есть следующие комбинации:\n" + a.toString());
            }
        }
    }
    class Tiles {
        ArrayList<Integer> mans;
        ArrayList<Integer> pins;
        ArrayList<Integer> sous;
        ArrayList<Integer> winds;
        ArrayList<Integer> dragons;
        ArrayList[] suits;
        Integer cur;
        boolean drags;
        boolean windsB;
        int c;
        HashSet<String> combinations = new HashSet<>();
        public Tiles(String[] tiles){
            mans = new ArrayList<>();
            pins = new ArrayList<>();
            sous = new ArrayList<>();
            winds = new ArrayList<>();
            dragons = new ArrayList<>();
            suits = new ArrayList[]{mans,pins,sous};
            //Ветра: 1-север, 2-юг, 3-запад, 4-восток
            //Драконы: 1-белый, 2-красный, 3-зеленый
            if (tiles[0].length() > 1) {
                for (int i = 0; i < tiles.length; i++) {
                    if (tiles[i].substring(0, tiles[i].length() - 1).equals("Man")) {
                        mans.add(Integer.parseInt(String.valueOf(tiles[i].charAt(tiles[i].length() - 1))));
                    } else if (tiles[i].substring(0, tiles[i].length() - 1).equals("Pin")) {
                        pins.add(Integer.parseInt(String.valueOf(tiles[i].charAt(tiles[i].length() - 1))));
                    } else if (tiles[i].substring(0, tiles[i].length() - 1).equals("Sou")) {
                        sous.add(Integer.parseInt(String.valueOf(tiles[i].charAt(tiles[i].length() - 1))));
                    } else if (tiles[i].equals("Haku")) {
                        dragons.add(1);
                    } else if (tiles[i].equals("Chan")) {
                        dragons.add(2);
                    } else if (tiles[i].equals("Hatsu")) {
                        dragons.add(3);
                    } else if (tiles[i].equals("Nan")) {
                        winds.add(2);
                    } else if (tiles[i].equals("Pei")) {
                        winds.add(1);
                    } else if (tiles[i].equals("Shaa")) {
                        winds.add(3);
                    } else if (tiles[i].equals("Ton")) {
                        winds.add(4);
                    }
                }
                findCombinations();
            }
        }
        public void findCombinations() {
            findPons("mans",mans.toArray());
            findPons("pins",pins.toArray());
            findPons("sous",sous.toArray());
            findPons("dragons",winds.toArray());
            findPons("winds",dragons.toArray());

            findChis("mans",mans.toArray());
            findChis("pins",pins.toArray());
            findChis("sous",sous.toArray());

            findKans("mans",mans.toArray());
            findKans("pins",pins.toArray());
            findKans("sous",sous.toArray());
            findKans("dragons",winds.toArray());
            findKans("winds",dragons.toArray());

        }
        public void findPons(String suit, Object[] a){
            switch (suit){
                case "mans":
                    suit = "Ман";
                    break;
                case "pins":
                    suit = "Пин";
                    break;
                case "sous":
                    suit = "Соу";
                    break;
                case "dragons":
                    drags = true;
                    break;
            }
            for (int i = 0; i < a.length; i++) {
                c = 1;
                cur = (Integer) a[i];
                if (drags) {
                    switch ((Integer) a[i]) {
                        case 1:
                            a[i] = "белых драконов";
                            break;
                        case 2:
                            a[i] = "красных драконов";
                            break;
                        case 3:
                            a[i] = "зеленых драконов";
                            break;
                    }
                }
                if (windsB){
                    switch ((Integer) a[i]) {
                        case 1:
                            a[i] = "северных ветров";
                            break;
                        case 2:
                            a[i] = "южных ветров";
                            break;
                        case 3:
                            a[i] = "западных ветров";
                            break;
                        case 4:
                            a[i] = "восточных ветров";
                            break;
                    }
                }
                for (int j = 0; j < a.length; j++) {
                    if (j == i){
                        continue;
                    }
                    if (a[j] == a[i]){
                        c++;
                    }
                    if (c == 3){
                        c = 1;
                        if (drags || windsB)
                            combinations.add("Пон из " + a[i]);
                        else
                            combinations.add("Пон из " + a[i] + " " + suit);
                    }
                }
            }
        }
        public void findChis(String suit, Object[] a){
            switch (suit){
                case "mans":
                    suit = "Ман";
                    break;
                case "pins":
                    suit = "Пин";
                    break;
                case "sous":
                    suit = "Соу";
                    break;
            }
            for (int i = 0; i < a.length; i++) {
                c = 1;
                cur = (Integer) a[i];
                for (int j = 0; j < a.length; j++) {
                    if (j == i){
                        continue;
                    }
                    if ((Integer) a[j] == (Integer)a[i] + c){
                        c++;
                    }
                    if (c == 3){
                        c = 1;
                        combinations.add("Чи из " + a[i] + "," + ((Integer)a[i] + 1) + "," + ((Integer)a[i] + 2) + " " + suit);
                    }
                }
            }
        }
        public void findKans(String suit, Object[] a){
            switch (suit){
                case "mans":
                    suit = "Ман";
                    break;
                case "pins":
                    suit = "Пин";
                    break;
                case "sous":
                    suit = "Соу";
                    break;
            }
            for (int i = 0; i < a.length; i++) {
                c = 1;
                cur = (Integer) a[i];
                for (int j = 0; j < a.length; j++) {
                    if (j == i){
                        continue;
                    }
                    if (a[j] == a[i]){
                        c++;
                    }
                    if (c == 4){
                        c = 1;
                        combinations.add("Кан из " + a[i] + " " + suit);
                    }
                }
            }
        }

        @Override
        public String toString(){
            String a = " ";
            Iterator<String> iterator = combinations.iterator();
            while (iterator.hasNext()) {
                if (a.equals(" "))
                    a = a.concat(iterator.next());
                else
                    a = a.concat(";\n" + iterator.next());
            }
            return a;
        }
    }
}
