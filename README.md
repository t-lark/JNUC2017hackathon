# JNUC2017hackathon
Have you ever had the recon delta blues?  Have you ever wished you could just simply get deltas back from changes? 

Why does recon have to always submit all the data every single time?   Well, wait no more.  This hacky hack of a project,
which you should never ever use in any environment, and it actually breaks functionality of the JSS can do this.   It can delta
the app on change, but it only delta's that app.  Come to find out in my testing you have to build an XML of all the applicaitons 
and PUT it to the device record.  

As you can see when I triggered the diff tool when I installed Chrome, it overwrites my entire applicaiton inventory, so you will have to build the entire XML from scratch and POST/PUT the entire thing to get all your applications.

![screen shot 2017-10-26 at 1 12 56 pm](https://user-images.githubusercontent.com/5223193/32076409-7d012332-ba65-11e7-93e9-a1255c86d4a2.png)

So this is, at best a poc of a hack.


