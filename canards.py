# CREATED 15/11/2021 by Elwen#7166 for the Dirtybiologystan country
# Feel free to use it and improve it !
# coin.

from PIL import Image, ImageOps, ImageChops
import sys

def diff_pixel(P1,P2):
    """
    P = (r,g,b)
    """
    diff_r = abs(P1[0]-P2[0])
    diff_g = abs(P1[1]-P2[1])
    diff_b = abs(P1[2]-P2[2])
    return diff_r + diff_g + diff_b

def is_canard(Grid,Body, Beak, Outer_Walls_inbox, Outer_Walls_outbox, Special_beak_check,x,y,xmax,ymax,threshold = 0):
    current = Grid[x,y]

    #TESTING SPACE
    if not((2<= x < xmax-2) and (0 <= y < ymax-3)):
        return threshold+1

    #BEAK
    (b1x,b1y) = Beak[0]
    (b2x,b2y) = Beak[1]
    matching_beak = (0 == diff_pixel( Grid[x+b1x,y+b1y], Grid[x+b2x,y+b2y] ))
    if not matching_beak:
        return threshold+1

    #DIFFERENCE beak and body
    matching_beak_and_body = (0 == diff_pixel( Grid[x+b1x,y+b1y], current ))
    if matching_beak_and_body :
        return threshold+1

    #BODY
    artefacts = 0
    for (dx,dy) in Body:
        if not ( 0 == diff_pixel( current, Grid[x+dx,y+dy] ) ):
            artefacts +=1
        if artefacts > threshold :
            return threshold+1
    
    #Testing outer walls inbox
    matching_owi = False
    for (dx,dy) in Outer_Walls_inbox:
        matching_owi = ( 0 == diff_pixel( current, Grid[x+dx,y+dy] ) )
        if matching_owi :
            return threshold+1

    #Testing outer walls outbox
    matching_owo = False
    for (dx,dy) in Outer_Walls_outbox:
        if 0<=x+dx<xmax and 0<=y+dy<ymax :
            matching_owo = ( 0 == diff_pixel( current, Grid[x+dx,y+dy] ) )
            if matching_owo :
                return threshold+1

    #Testing special beak cases 
    matching_spc = False
    for (dx,dy) in Special_beak_check:
        if 0<=x+dx<xmax and 0<=y+dy<ymax :
            matching_spc = ( 0 == diff_pixel( Grid[x+b1x,y+b1y], Grid[x+dx,y+dy] ) )
            if matching_spc :
                return threshold+1
    return artefacts

def translate(X,Y,r,m):
    if r == 0:
        x = X-3
        y = Y-1
    elif r == 90:
        x = X-1
        y = Y-3
    elif r ==180:
        x = X-3
        y = Y-5
    else:
        x = X-4
        y = Y-3
    if m !=0:
        tmp = x
        x = y 
        y = x
    return x,y

def rotate_symetrize_pixel(x,y,angle,s,centre=(3,3),pat_size=7):
    #Symmetrize
    if s!=0:
        x = -x+pat_size-1
    #change to centre coordinate:
    (xc,yc)=sub_tuple((x,y),centre)
    #Rotation around the centre (origin)
    if angle==90:
        xc,yc = (-yc,xc)
    if angle==180:
        xc,yc = (-xc,-yc)
    if angle==270:
        xc,yc = (yc,-xc)
    #back to image coordinates :
    return add_tuple((xc,yc),centre)

def sub_tuple(T2,T1):
    """
    T2-T1
    """
    return (T2[0]-T1[0],T2[1]-T1[1])

def add_tuple(T1,T2):
    return (T2[0]+T1[0],T2[1]+T1[1])

def load_pattern(file_name,r=0,m=0):
    im_pat = Image.open(file_name)
    if m == 1:
        im_pat = ImageOps.mirror(im_pat)
    im_pat = im_pat.rotate(r)
    #im_pat.save(str(r)+".png")
    Pat = im_pat.load()
    xpmax = im_pat.size[0]
    ypmax = im_pat.size[1]
    body = []
    beak = []
    outer_Walls_inbox = []
    outer_Walls_outbox = []
    special_beak_check = []
    for X in range(xpmax):
        for Y in range(ypmax):
            pixel = Pat[X,Y]
            x,y = translate(X,Y,r,m)
            if (x!= 0 or y !=0) and (pixel != (255,255,255)):
                if pixel == (255,255,0): # Corps = Jaune
                    body.append((x,y))
                if pixel == (0,0,0): # Bec = Noir
                    beak.append((x,y))
                if pixel[2] == 255: #Bordure interieure = Bleu clair
                    outer_Walls_inbox.append((x,y))
                if pixel == (0,0,170): #Bordure exterieure = Bleu fonce
                    outer_Walls_outbox.append((x,y))
                if pixel[0] == 0 and pixel[1] > 0:
                    special_beak_check.append((x,y))
    
    #if r == 180:
    #    print(body, beak, outer_Walls_inbox, outer_Walls_outbox, special_beak_check,sep='\n')
    im_pat.close()
    return body, beak, outer_Walls_inbox, outer_Walls_outbox, special_beak_check

def find_pattern(image_file_name,pattern_files_names,tolerance=0,check_symmetry =1,check_rotations=1,output_file =None,output_png_file = None):
    im = Image.open(image_file_name)
    Grid = im.load()
    xmax = im.size[0]
    ymax = im.size[1]

    if output_png_file is not None:
        img  = im.copy()#Image.new( mode = "RGB", size = (xmax, ymax), color = (230, 230, 230) )
        for x in range (xmax):
            for y in range (ymax):
                img.putpixel((x, y), (200, 200, 200))
    if output_file is not None:
        txt_file = open(output_file,"w") 

    nb_total_coin = 0
    for i,pat_file in enumerate(pattern_files_names):
        print("Forme",i+1,":",pat_file.split(".")[0])
        for mirror in range(check_symmetry+1):
            if mirror == 0:
                print("  Sans symetrie")
            else:
                print("  Avec symetrie")
            for rot in range(check_rotations*3+1):
                if output_file is not None:
                    txt_file.write("\n-------\n"+pat_file.split(".")[0]+";symmetry"+str(mirror)+";angle"+str(rot)+'\n') 
                nb_coin = 0
                Body, Beak, Outer_Walls_inbox, Outer_Walls_outbox, Special_beak_check = load_pattern(pat_file,r=rot*90,m=mirror)
                for x in range (xmax):
                    for y in range (ymax):
                            artefacts = is_canard(Grid,Body, Beak, Outer_Walls_inbox, Outer_Walls_outbox, Special_beak_check,x,y,xmax,ymax,threshold =tolerance)
                            if artefacts<=tolerance:
                                #canard trouve
                                nb_coin+=1
                                if output_file is not None:
                                    if artefacts==0:
                                        txt_file.write(str(x)+","+str(y)+'\n') 
                                    else:
                                        txt_file.write(str(x)+","+str(y)+" artefacts : "+str(artefacts)+'\n') 
                                if output_png_file is not None:
                                    for (dx,dy) in Body:
                                        img.putpixel((x+dx, y+dy), (0, 0, 0))
                                    for (dx,dy) in Beak:
                                        img.putpixel((x+dx, y+dy), (0, 0, 0))
                                    img.putpixel((x, y), (0, 0, 0))
                                
                print("    Angle",rot*90,":",nb_coin,"canards")
                nb_total_coin += nb_coin
    print("Nombre total de canards :",nb_total_coin)
    if output_file is not None:
        txt_file.write('\n-------\nTOTAL : '+str(nb_total_coin))
        txt_file.close()
    if output_png_file is not None:
        diff = ImageChops.subtract(im, img)
        img.save(output_png_file)
        diff.save("diff"+output_png_file)
        img.close()
        diff.close()
    im.close()

if __name__ == "__main__":
    if len(sys.argv)<3:
        print("USAGE : python canards.py drapeau.png pattern1 <pattern2> ...")
        print("optionnal : -tolerance=integer")
        sys.exit(0)
    for arg_id,arg in enumerate(sys.argv):
        if "-tolerance" in arg:
            tolerance = int(sys.argv.pop(arg_id).split("=")[1])
        else:
            tolerance=0
    im_name = sys.argv[1]
    patterns = sys.argv[2:]
    print(rotate_symetrize_pixel(5,2,90,1,centre=(3,3),pat_size=7))
    #find_pattern(im_name,patterns,tolerance=tolerance,check_symmetry=1,check_rotations=1,output_file = "canard.txt",output_png_file="canards.png") #"drapeau19-11-21.png"
